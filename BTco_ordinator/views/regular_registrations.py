from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTco_ordinator.forms import RegistrationsUploadForm, RegistrationsFinalizeEventForm
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTCycleCoordinator
from BTco_ordinator.models import BTRollLists_Staging, BTRollLists, BTStudentRegistrations_Staging, BTStudentRegistrations, BTSubjects, BTNotRegistered
from BThod.models import BTCoordinator
from django.db.models import Q
from django.db import transaction
from BTsuperintendent.user_access_test import registration_access

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def btech_regular_registration(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if(request.method=='POST'):
        form = RegistrationsUploadForm(regIDs, request.POST)
        if(form.is_valid()):
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,byear,bsem,dept,mode, regulation) = regIDs[int(form.cleaned_data['regID'])]
                event = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation).first()
                not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem,\
                    Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                mode = 1
                if(byear==1):
                    rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', flat=True))
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
                    for roll in rolls:
                        for sub in subs:
                            if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                                regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                                regRow.save()
                    BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                else:
                    rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', values=True))
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'msg':msg})
                    subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'msg':msg})
                    initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
                    for roll in rolls:
                        for sub in subs:
                            if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                                regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                                regRow.save()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
                    return render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
    else:
        form = RegistrationsUploadForm(Options=regIDs)
    return(render(request, 'BTco_ordinator/BTRegularRegistrationUpload.html',{'form':form }))

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def registrations_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=0, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=0, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if(request.method=='POST'):
        form = RegistrationsFinalizeEventForm(regIDs, request.POST)
        if(form.is_valid()):
            currentRegEvent = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
            currentRegEventId = currentRegEvent.id
            regs = BTStudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId).exclude(sub_id__course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC'])
            rolllist = BTRollLists.objects.filter(RegEventId_id=currentRegEventId)
            for reg in regs:
                roll = rolllist.filter(student=reg.student.student).first()
                if not BTStudentRegistrations.objects.filter(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id).exists():
                    s=BTStudentRegistrations(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                    s.save()
            currentRegEvent.RegistrationStatus = 0
            oesubs = BTSubjects.objects.filter(RegEventId=currentRegEventId,course__CourseStructure__Category__in=['OEC','OPC'])
            if len(oesubs) == 0:
                currentRegEvent.OERegistartionStatus=0
            currentRegEvent.save()
            return render(request, 'BTco_ordinator/BTRegistrationsFinalizeSuccess.html')
    else:
        form = RegistrationsFinalizeEventForm(regIDs)
    return render(request, 'BTco_ordinator/BTRegistrationsFinalize.html',{'form':form})
    
