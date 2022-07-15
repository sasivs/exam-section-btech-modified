from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from superintendent.user_access_test import registration_access
from co_ordinator.forms import DeptElectiveRegsForm
from co_ordinator.models import RollLists_Staging, Subjects, StudentRegistrations_Staging
from superintendent.models import RegistrationStatus, CycleCoordinator
from hod.models import Coordinator


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_all(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear,Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1,Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    subjects=[]
    if(request.method == "POST"):
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2,'III':3,'IV':4}
        regId = request.POST['regID']
        subId = request.POST['subId']
        data = {'regID':regId, 'subId':subId}
        form = DeptElectiveRegsForm(regIDs,subjects,data)
        if regId != '--Choose Event--' and subId != '--Select Subject--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id

            rolls = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
            for i in rolls:
                reg = StudentRegistrations_Staging(RegNo=i.student.RegNo, RegEventId=currentRegEventId, Mode=1,sub_id=subId)
                reg.save()
            rolls = rolls.values_list('student__RegNo', flat=True)
            StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId).exclude(RegNo__in=rolls).delete()
            return render(request, 'co_ordinator/Dec_Regs_success.html')
        elif regId != '--Choose Event--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            subjects = Subjects.objects.filter(RegEventId=currentRegEventId, Category='DEC')
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            form = DeptElectiveRegsForm(regIDs,subjects,data)
    else:
        form = DeptElectiveRegsForm(regIDs)
    return render(request, 'co_ordinator/Dec_register_all.html',{'form':form})