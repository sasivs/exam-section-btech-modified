from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTExamStaffDB.models import BTStudentInfo
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import MakeupRegistrationsForm
from BTco_ordinator.models import BTStudentRegistrations_Staging, BTStudentMakeups, BTRollLists, BTRollLists_Staging, BTSubjects,\
     BTStudentRegistrations
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTCycleCoordinator
from BTExamStaffDB.models import BTStudentInfo
from BThod.models import BTCoordinator
from django.db import transaction

@transaction.atomic
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
    if request.method == 'POST' and request.POST.get('RegEvent'):
        event = BTRegistrationStatus.objects.filter(id=request.POST.get('RegEvent')).first()
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
        elif request.POST.get('RegNo') and 'Submit' not in request.POST.keys():
            roll = BTRollLists_Staging.objects.filter(id=request.POST.get('RegNo')).first()
            already_registered = BTStudentRegistrations_Staging.objects.filter(student=roll, \
                        RegEventId_id=event.id)
            modes_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in already_registered}
            from json import dumps
            return render(request, 'BTco_ordinator/MakeupRegistrations.html', {'form':form, 'modes':dumps(modes_selection)})
        elif request.POST.get('RegNo') and 'Submit' in request.POST.keys() and form.is_valid():
            roll = BTRollLists_Staging.objects.filter(id=form.cleaned_data.get('RegNo')).first()
            already_registered = BTStudentRegistrations_Staging.objects.filter(student=roll, RegEventId_id=event.id)
            for sub in form.myFields:
                if form.cleaned_data['Check'+str(sub[8])]:
                    if not already_registered.filter(sub_id_id=sub[8]):
                        newReg = BTStudentRegistrations_Staging(student=roll, sub_id_id=sub[8],\
                            Mode=form.cleaned_data['RadioMode'+str(sub[8])], RegEventId_id=event.id)
                        newReg.save()
                else:
                    if already_registered.filter(sub_id_id=sub[8]):
                        BTStudentRegistrations_Staging.objects.get(id=already_registered.filter(sub_id_id=sub[8]).first().id).delete()
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
        if not BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8]).exists():
            registration_obj = BTStudentRegistrations_Staging(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
            registration_obj.save()
    return "Completed!!"

def add_makeup_rolls(file):
    import pandas as pd
    file = pd.read_excel(file)
    for rIndex, row in file.iterrows():
        print(row)
        regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
        student_obj = BTStudentInfo.objects.filter(RegNo=row[7]).first()
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
            # regEvent = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[3], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode='R').first()
            # subject_id = BTSubjects.objects.filter(RegEventId_id=regEvent.id, SubCode=row[7]).first()
            regular_reg = BTStudentRegistrations.objects.filter(RegNo=row[9], RegEventId__Mode='R', sub_id__SubCode=row[7]).first()
            subject_id = regular_reg.sub_id
            regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
            student = BTRollLists_Staging.objects.filter(student__RegNo=row[9], RegEventId_id=regEventId.id).first()
            if not BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).exists():
                registration_obj = BTStudentRegistrations_Staging(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).update(Mode=row[8])
            if not BTStudentRegistrations.objects.filter(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.id).exists():
                registration_obj = BTStudentRegistrations(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.id).update(Mode=row[8])
        else:
            regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
            subject_id = makeups.filter(SubCode=row[7]).first()
            student = BTRollLists_Staging.objects.filter(student__RegNo=row[9], RegEventId_id=regEventId.id).first()
            if not BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).exists():
                registration_obj = BTStudentRegistrations_Staging(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).update(Mode=row[8])
            if not BTStudentRegistrations.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).exists():
                registration_obj = BTStudentRegistrations(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
                registration_obj.save()
            else:
                BTStudentRegistrations.objects.filter(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).update(Mode=row[8])
    return "Completed!!"
