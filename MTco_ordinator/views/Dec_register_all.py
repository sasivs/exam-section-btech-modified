from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from MTsuperintendent.user_access_test import registration_access
from MTco_ordinator.forms import DeptElectiveRegsForm
from MTco_ordinator.models import MTRollLists_Staging, MTSubjects, MTStudentRegistrations_Staging
from MTsuperintendent.models import MTRegistrationStatus
from MThod.models import MTCoordinator


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_all(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear,Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]

    necessary_field_msg = False
    subjects=[]
    if(request.method == "POST"):
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2}
        regId = request.POST['regID']
        subId = request.POST['subId']
        data = {'regID':regId, 'subId':subId}
        form = DeptElectiveRegsForm(subjects,data)
        if regId != '--Choose Event--' and subId != '--Select Subject--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            rolls = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
            for i in rolls:
                reg = MTStudentRegistrations_Staging(RegNo=i.student.RegNo, RegEventId=currentRegEventId, Mode=1,sub_id=subId)
                reg.save()
            rolls = rolls.values_list('student__RegNo', flat=True)
            MTStudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId).exclude(RegNo__in=rolls).delete()
            return render(request, 'MTco_ordinator/Dec_Regs_success.html')
        elif regId != '--Choose Event--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            subjects = MTSubjects.objects.filter(RegEventId=currentRegEventId, Category='DEC')
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            print(subjects)
            form = DeptElectiveRegsForm(subjects,data)
    else:
        form = DeptElectiveRegsForm(regIDs)
    return render(request, 'MTco_ordinator/Dec_register_all.html',{'form':form})
