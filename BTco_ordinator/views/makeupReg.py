from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTsuperintendent.user_access_test import registration_access
from BTco_ordinator.forms import MakeupRegistrationsForm
from BTco_ordinator.models import BTStudentRegistrations_Staging, BTStudentMakeups, BTRollLists, BTRollLists_Staging, BTSubjects,\
     BTStudentRegistrations
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTCycleCoordinator
from BTExamStaffDB.models import BTStudentInfo
from BThod.models import BTCoordinator

@login_required(login_url="/login/")
@user_passes_test(registration_access)
def makeup_registrations(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear,Mode='M')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1,Mode='M')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if request.method == 'POST' and request.POST['RegEvent'] != '-- Select Registration Event --':
        regId = request.POST['RegEvent']
        strs = regId.split(':')
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2,'III':3,'IV':4}
        strs = regId.split(':')
        dept = deptDict[strs[0]]
        ayear = int(strs[3])
        asem = int(strs[4])
        byear = rom2int[strs[1]]
        bsem = rom2int[strs[2]]
        regulation = int(strs[5])
        mode = strs[6]
        currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
        currentRegEventId = currentRegEventId[0].id
        con = {} 
        if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
            con['RegEvent']=request.POST['RegEvent']
            if 'RegNo' in request.POST.keys():
                con['RegNo']=request.POST['RegNo']
            form = MakeupRegistrationsForm(regIDs,con)
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
            form = MakeupRegistrationsForm(regIDs,request.POST)
        if 'RegNo' not in request.POST.keys() :
            pass
        elif request.POST['RegNo'] != '--Select Reg Number--' and 'Submit' not in request.POST.keys():
            already_registered = BTStudentRegistrations_Staging.objects.filter(RegNo=request.POST['RegNo'], \
                        RegEventId_id=currentRegEventId)
            modes_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in already_registered}
            from json import dumps
            return render(request, 'BTco_ordinator/MakeupRegistrations.html', {'form':form, 'modes':dumps(modes_selection)})
        elif request.POST['RegNo'] != '--Select Reg Number--' and 'Submit' in request.POST.keys() and form.is_valid():
            for sub in form.myFields:
                already_registered = BTStudentRegistrations_Staging.objects.filter(RegNo=request.POST['RegNo'], \
                        sub_id_id=sub[8], RegEventId_id=currentRegEventId)
                if form.cleaned_data['Check'+str(sub[8])]:
                    if len(already_registered) == 0:
                        newReg = BTStudentRegistrations_Staging(RegNo=request.POST['RegNo'], sub_id_id=sub[8],\
                            Mode=form.cleaned_data['RadioMode'+str(sub[8])], RegEventId_id=currentRegEventId)
                        newReg.save()
                else:
                    if len(already_registered) != 0:
                        BTStudentRegistrations_Staging.objects.get(id=already_registered[0].id).delete()
            return render(request, 'BTco_ordinator/MakeupRegistrationsSuccess.html')
    elif request.method == 'POST':
        form = MakeupRegistrationsForm(regIDs,request.POST)
    else:
        form = MakeupRegistrationsForm(regIDs)
    return render(request, 'BTco_ordinator/MakeupRegistrations.html', {'form':form})


def add_makeup_regs(file):
    import pandas as pd
    file = pd.read_excel(file)
    for rIndex, row in file.iterrows():
        print(row)
        makeups = BTStudentMakeups.objects.filter(RegNo=row[9], BYear=row[2], Dept=row[4])
        regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
        subject_id = makeups.filter(SubCode=row[7]).first()
        if not BTStudentRegistrations_Staging.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8]).exists():
            registration_obj = BTStudentRegistrations_Staging(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
            registration_obj.save()
    return "Completed!!"

def add_makeup_rolls(file):
    import pandas as pd
    file = pd.read_excel(file)
    for rIndex, row in file.iterrows():
        print(row)
        regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
        student_obj = BTStudentInfo.objects.filter(RegNo=row[8]).first()
        if not BTRollLists_Staging.objects.filter(student_id=student_obj.id, RegEventId_id=regEventId.id).exists():
            roll = BTRollLists_Staging(student_id=student_obj.id, RegEventId_id=regEventId.id, Cycle=row[4], Section='NA')
            roll.save()
            f_roll = BTRollLists(student_id=student_obj.id, RegEventId_id=regEventId.id, Cycle=row[4], Section='NA')
            f_roll.save()
    return "Completed!!"
    
def add_makeup_regs_r_grade(file):
    import pandas as pd
    file = pd.read_excel(file)
    for rIndex, row in file.iterrows():
        print(row)
        makeups = BTStudentMakeups.objects.filter(RegNo=row[9], BYear=row[2], Dept=row[4])
        if not makeups.filter(SubCode=row[7]).exists():
            regEvent = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[3], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode='R').first()
            subject_id = BTSubjects.objects.filter(RegEventId_id=regEvent.id, SubCode=row[7]).first()
            regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
            if not BTStudentRegistrations_Staging.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).exists():
                registration_obj = BTStudentRegistrations_Staging(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations_Staging.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).update(Mode=row[8])
            if not BTStudentRegistrations.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).exists():
                registration_obj = BTStudentRegistrations(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).update(Mode=row[8])
        else:
            regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
            subject_id = makeups.filter(SubCode=row[7]).first()
            if not BTStudentRegistrations_Staging.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).exists():
                registration_obj = BTStudentRegistrations_Staging(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations_Staging.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).update(Mode=row[8])
            if not BTStudentRegistrations.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).exists():
                registration_obj = BTStudentRegistrations(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).update(Mode=row[8])
    return "Completed!!"
