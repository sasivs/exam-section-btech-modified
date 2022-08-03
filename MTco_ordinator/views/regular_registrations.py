from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTco_ordinator.forms import RegistrationsUploadForm, RegistrationsFinalizeEventForm
from MTsuperintendent.models import MTRegistrationStatus
from MTco_ordinator.models import MTRollLists_Staging, MTStudentRegistrations_Staging, MTStudentRegistrations, MTSubjects
from MThod.models import MTCoordinator
from django.db.models import Q
from MTsuperintendent.user_access_test import registration_access


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def mtech_regular_registration(request):
    
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear, Mode='R')
    
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
   
    if(request.method=='POST'):
        form = RegistrationsUploadForm(regIDs, request.POST)
        if(form.is_valid()):
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,myear,msem,dept,mode,regulation) = regIDs[int(form.cleaned_data['regID'])]
                currentRegEventId=MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId=currentRegEventId[0].id
                mode=1
                if(myear==1):
                    rolls = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    subs = MTSubjects.objects.filter(~Q(Category='OEC'),RegEventId=currentRegEventId).filter(~Q(Category='DEC'))
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                    initial_registrations=MTStudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId,Mode=1)
                    for roll in rolls:
                        for sub in subs:
                          if not initial_registrations.filter(RegNo=roll.student.RegNo,sub_id=sub.id).exists():
                            regRow = MTStudentRegistrations_Staging(RegNo=roll.student.RegNo, Mode=mode, sub_id=sub.id,RegEventId=currentRegEventId)
                            regRow.save()
                    MTStudentRegistrations_Staging.objects.filter(~Q(RegNo__in=rolls.values_list('student__RegNo',flat=True)),RegEventId=currentRegEventId).delete()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    return render(request, 'co_ordinator/BTRegularRegistrationUpload.html', {'form':form, 'msg':msg})
                else:
                    rolls = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
                    if len(rolls)==0:
                        msg = 'There is no roll list for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUploadSuccess.html', {'msg':msg})
                    subs = MTSubjects.objects.filter(~Q(Category='OEC'),RegEventId=currentRegEventId).filter(~Q(Category='DEC'))
                    if len(subs)==0:
                        msg = 'There are no subjects for the selected registration event.'
                        return render(request, 'co_ordinator/BTRegularRegistrationUploadSuccess.html', {'msg':msg})
                    initial_registrations=MTStudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId,Mode=1)
                    for roll in rolls:
                        for sub in subs:
                          if not initial_registrations.filter(RegNo=roll.student.RegNo,sub_id=sub.id).exists():
                            regRow = MTStudentRegistrations_Staging(RegNo=roll.student.RegNo, Mode=mode, sub_id=sub.id,RegEventId=currentRegEventId)
                            regRow.save()
                    msg = 'Your data upload for Student Registrations has been done successfully.'
                    MTStudentRegistrations_Staging.objects.filter(~Q(RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId=currentRegEventId).delete()
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
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear)
    
    if(request.method=='POST'):
        form = RegistrationsFinalizeEventForm(regIDs,request.POST)
        if(form.is_valid()):
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
            years = {1:'I',2:'II'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2}
            if(form.cleaned_data['regID']!='--Choose Event--'):
                strs = form.cleaned_data['regID'].split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                myear = rom2int[strs[1]]
                msem = rom2int[strs[2]]
                regulation=int(strs[5])
                mode = strs[6]
                regs = []
                
                currentRegEvent=MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,Dept=dept,Mode=mode,Regulation=regulation).first()
                currentRegEventId=currentRegEvent.id
                regs = MTStudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId)
                for reg in regs:
                    s=MTStudentRegistrations(RegNo=reg.RegNo, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                    s.save()
                currentRegEvent.RegistrationStatus = 0
                currentRegEvent.save()
                return render(request, 'co_ordinator/BTRegistrationsFinalizeSuccess.html')
    else:
        form = RegistrationsFinalizeEventForm(regIDs)
    return render(request, 'co_ordinator/BTRegistrationsFinalize.html',{'form':form})
