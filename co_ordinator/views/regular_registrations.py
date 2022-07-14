from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from co_ordinator.forms import RegistrationsUploadForm, RegistrationsFinalizeEventForm
from superintendent.models import RegistrationStatus, CycleCoordinator
from co_ordinator.models import RollLists_Staging, StudentRegistrations_Staging, StudentRegistrations, Subjects
from hod.models import Coordinator
from django.db.models import Q
from superintendent.user_access_test import registration_access


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def btech_regular_registration(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if(request.method=='POST'):
        form = RegistrationsUploadForm(regIDs, request.POST)
        if(form.is_valid()):
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,byear,bsem,dept,mode, regulation) = regIDs[int(form.cleaned_data['regID'])]
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                mode = 1
                if(byear==1):
                    rolls = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    subs = Subjects.objects.filter(~Q(Category='OEC'),RegEventId=currentRegEventId).filter(~Q(Category='DEC'))
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    initial_registrations = StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId, Mode=1)
                    for roll in rolls:
                        for sub in subs:
                            if not initial_registrations.filter(RegNo=roll.student.RegNo, sub_id=sub.id).exists():
                                regRow = StudentRegistrations_Staging(RegNo=roll.student.RegNo, Mode=mode, RegEventId=currentRegEventId, sub_id=sub.id)
                                regRow.save()
                    StudentRegistrations_Staging.objects.filter(~Q(RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId=currentRegEventId).delete()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                else:
                    rolls = RollLists_Staging.objects.filter(RegEvent_id=currentRegEventId)
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUploadSuccess.html', {'msg':msg})
                    subs = Subjects.objects.filter(~Q(Category='OEC'),RegEventId=currentRegEventId).filter(~Q(Category='DEC'))
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUploadSuccess.html', {'msg':msg})
                    initial_registrations = StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId, Mode=1)
                    for roll in rolls:
                        for sub in subs:
                            if not initial_registrations.filter(RegNo=roll.student.RegNo, sub_id=sub.id).exists():
                                regRow = StudentRegistrations_Staging(RegNo=roll.student.RegNo, Mode=mode, RegEventId=currentRegEventId, sub_id=sub.id)
                                regRow.save()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    StudentRegistrations_Staging.objects.filter(~Q(RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId=currentRegEventId).delete()
                    return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
    else:
        form = RegistrationsUploadForm(Options=regIDs)
    return(render(request, 'co_ordinator/BTRegularRegistrationUpload.html',{'form':form }))


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def registrations_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if(request.method=='POST'):
        form = RegistrationsFinalizeEventForm(regIDs, request.POST)
        if(form.is_valid()):
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            if(form.cleaned_data['regID']!='--Choose Event--'):
                strs = form.cleaned_data['regID'].split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                regulation=int(strs[5])
                mode = strs[6]
                regs = []
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                regs = StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId)

                for reg in regs:
                    # if not StudentRegistrations.objects.filter(RegNo=reg.RegNo, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id).exists():
                    s=StudentRegistrations(RegNo=reg.RegNo, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                    s.save() 
                return render(request, 'co_ordinator/BTRegistrationsFinalizeSuccess.html')
    else:
        form = RegistrationsFinalizeEventForm(regIDs)
    return render(request, 'co_ordinator/BTRegistrationsFinalize.html',{'form':form})
    
