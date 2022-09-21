
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from BTco_ordinator.forms import RollListStatusForm, RollListRegulationDifferenceForm,\
     RollListFinalizeForm, GenerateRollListForm, RollListsCycleHandlerForm, RollListStatusForm, UpdateSectionInfoForm, UploadSectionInfoForm,\
        RollListFeeUploadForm, NotRegisteredStatusForm
from BTco_ordinator.models import BTRollLists_Staging, BTRollLists, BTRollLists_Staging, BTRegulationChange, BTStudentBacklogs, BTNotRegistered
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTCycleCoordinator, BTHOD
from BTExamStaffDB.models import BTStudentInfo 
from BThod.models import BTCoordinator
from BTco_ordinator.models import BTNotPromoted, BTStudentRegistrations_Staging,  BTStudentMakeups, BTDroppedRegularCourses
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from BTsuperintendent.user_access_test import roll_list_access, roll_list_status_access

@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def generateRollList(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if request.method == 'POST':
        if 'Regulation_change' in request.POST:
            (ayear,asem,byear,bsem,regulation)=request.session.get('ayasbybsr')
            if(byear ==1):
                not_promoted_regno = request.session.get('not_promoted_regno_firstyear')  
            else:
                not_promoted_regno = request.session.get('not_promoted_regno')
                
            
            not_promoted_regnos =[]
            ayasbybsr = (ayear,asem,byear,bsem,regulation)
            form = RollListRegulationDifferenceForm((not_promoted_regno,regulation),request.POST)
           
            if(form.is_valid()):
        
                for cIndex, sReg in enumerate(not_promoted_regno):
                    if(form.cleaned_data.get('RadioMode'+str(sReg))):
                        choice = form.cleaned_data.get('RadioMode'+str(sReg))
                        
                        s_info = BTStudentInfo.objects.get(RegNo=sReg)
                        if(choice == 'YES'):
                            if(byear ==1):
                                not_promoted_regnos.append(sReg)
                            else:
                                roll = BTRollLists_Staging.objects.filter(student=s_info, RegEventId_id=request.session.get('currentRegEventId'))
                                if(len(roll) == 0):
                                    roll = BTRollLists_Staging(student=s_info, RegEventId_id=request.session.get('currentRegEventId'))
                                    roll.save()
                            prev_regulation  = s_info.Regulation
                            s_info.Regulation = regulation
                            s_info.save()
                            if(prev_regulation != regulation):
                                currentRegEventId = request.session.get('currentRegEventId')
                                regu_change = BTRegulationChange(RegEventId_id = currentRegEventId, student= s_info, \
                                    PreviousRegulation=prev_regulation ,PresentRegulation=regulation)
                                regu_change.save()
                        else:
                            BTRollLists_Staging.objects.filter(student__RegNo=sReg, RegEventId_id=request.session.get('currentRegEventId')).delete()
                
                if(len(not_promoted_regnos)!=0 and byear ==1 ):
                        request.session['not_promoted_regno'] = (not_promoted_regnos)
                        request.session['ayasbybsr'] = ayasbybsr
                        request.session['currentRegEventId'] = request.session.get('currentRegEventId')
                        return HttpResponseRedirect(reverse('BTFirstYearRollListsCycleHandler' ))
                return (render(request, 'BTco_ordinator/RollListGenerateSuccess.html')) 
            
        else:
            form = GenerateRollListForm(regIDs, request.POST)
            if(form.is_valid()):
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I',2:'II',3:'III',4:'IV'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                # print(form.cleaned_data['regID'])
                if(form.cleaned_data['regID']!='--Choose Event--'):
                    strs = form.cleaned_data['regID'].split(':')
                    dept = deptDict[strs[0]]
                    ayear = int(strs[3])
                    asem = int(strs[4])
                    byear = rom2int[strs[1]]
                    bsem = rom2int[strs[2]]
                    regulation = int(strs[5])
                    ayasbybsr = (ayear,asem,byear,bsem,regulation)
                    mode = strs[6]
                    currentRegEvent = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation).first()
                    currentRegEvent.RollListFeeStatus = 0
                    currentRegEvent.save()
                    currentRegEvent = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation)
                    currentRegEventId = currentRegEvent[0].id
                    BTNotRegistered.objects.filter(RegEventId_id=currentRegEventId).delete()
                    if mode == 'R':
                        if(byear==1):
                            reg_rgs = BTStudentInfo.objects.filter(AdmissionYear=ayear,Cycle=dept,Regulation=regulation)
                            not_prom_regs = BTNotPromoted.objects.filter(AYear=ayear-1,BYear=1, PoA='R')
                            related_events = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                                Mode=mode)
                            not_prom_regs_copy = BTNotPromoted.objects.filter(AYear=ayear-1,BYear=1, PoA='R')
                            for not_prom_reg in not_prom_regs:
                                if BTRollLists_Staging.objects.filter(student__RegNo=not_prom_reg.student.RegNo, RegEventId_id__in=related_events.values_list('id', flat=True)).exists():
                                    not_prom_regs_copy.exclude(student__RegN0=not_prom_reg.student.RegNo)
                            
                            regular_regd_no = list(reg_rgs.values_list('RegNo', flat=True))
                            not_prom_regs = [row.student.RegNo for row in not_prom_regs_copy]

                            valid_rolls = regular_regd_no+not_prom_regs

                            initial_roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                            BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_rolls), RegEventId_id=currentRegEventId).delete()


                            for row in reg_rgs:
                                if not initial_roll_list.filter(student=row, Cycle=row.Cycle).exists():
                                    roll = BTRollLists_Staging(student=row, Cycle=row.Cycle, RegEventId_id=currentRegEventId)
                                    roll.save()
                        
                            if(len( not_prom_regs) !=0):
                                regulation_form = RollListRegulationDifferenceForm(Options = (not_prom_regs,regulation))
                                request.session['not_promoted_regno_firstyear'] = not_prom_regs
                                request.session['ayasbybsr'] = ayasbybsr
                                request.session['currentRegEventId'] = currentRegEventId
                                return render(request, 'BTco_ordinator/generateRollList.html',{'form':form, 'regulation_form':regulation_form})
                            return (render(request, 'BTco_ordinator/RollListGenerateSuccess.html'))

                                
                        else:
                            if byear==2:
                                prev_regEventId = BTRegistrationStatus.objects.filter(AYear=ayear-1, BYear=byear-1, Regulation=regulation, Mode=mode)
                            else:
                                prev_regEventId = BTRegistrationStatus.objects.filter(AYear=ayear-1, BYear=byear-1, Regulation=regulation, Mode=mode, Dept=dept)  
                            present_not_prom_regs = BTNotPromoted.objects.filter(AYear=ayear-1,BYear=byear)
                            not_promoted_bmode = BTNotPromoted.objects.filter(AYear=ayear-2, BYear=byear-1, PoA='B')
                            not_promoted_regs = present_not_prom_regs | not_promoted_bmode
                            prev_not_prom_regs = BTNotPromoted.objects.filter(AYear=ayear-1, BYear=byear-1)
                            prev_not_prom_regd_no = prev_not_prom_regs.values_list('student__RegNo', flat=True)
                            prev_not_prom_regs = prev_not_prom_regs.values_list('student', flat=True)
                            reg_rgs = BTRollLists_Staging.objects.filter(~Q(student__in=prev_not_prom_regs), RegEventId__in=prev_regEventId, student__Dept=dept)
                            not_promoted_regno=[row.student.RegNo for row in not_promoted_regs]

                            regular_regd_no = reg_rgs.values_list('student__RegNo', flat=True)
                            valid_rolls = list(regular_regd_no) + not_promoted_regno
                            
                            initial_roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                            BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_rolls), RegEventId_id=currentRegEventId).delete()

                            for reg in reg_rgs:
                                if not initial_roll_list.filter(student=reg.student).exists():
                                    roll = BTRollLists_Staging(student=reg.student, RegEventId_id=currentRegEventId)
                                    roll.save()
                            
                            BTStudentRegistrations_Staging.objects.filter(RegNo__in=prev_not_prom_regd_no,RegEventId=currentRegEventId).delete()
                            BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId, student__in=prev_not_prom_regs).delete()

                            
                            if(len(not_promoted_regno) != 0):
                                request.session['not_promoted_regno'] = not_promoted_regno
                                request.session['ayasbybsr'] = ayasbybsr
                                request.session['currentRegEventId'] = currentRegEventId
                                regulation_form = RollListRegulationDifferenceForm(Options = (not_promoted_regno,regulation))
                                return render(request, 'BTco_ordinator/generateRollList.html',{'form':form,'regulation_form':regulation_form })

                    elif mode == 'B':

                        initial_roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                        if byear == 1:

                            backlog_rolls = BTStudentBacklogs.objects.filter(BYear=byear, BSem=bsem, Dept=dept).exclude(AYASBYBS__startswith=ayear).values_list('RegNo', flat=True)
                            backlog_rolls = list(set(backlog_rolls))
                            backlog_rolls.sort()

                            for regd_no in backlog_rolls:
                                student = BTStudentInfo.objects.get(RegNo=regd_no)
                                if not initial_roll_list.filter(student=student, Cycle=dept).exists():
                                    roll = BTRollLists_Staging(RegEventId_id=currentRegEventId, student=student, Cycle=dept)
                                    roll.save()
                        else:

                            backlog_rolls = BTStudentBacklogs.objects.filter(BYear=byear, Dept=dept, BSem=bsem).exclude(AYASBYBS__startswith=ayear).values_list('RegNo', flat=True)
                            backlog_rolls = list(set(backlog_rolls))
                            backlog_rolls.sort()

                            for regd_no in backlog_rolls:
                                student = BTStudentInfo.objects.get(RegNo=regd_no) 
                                if not initial_roll_list.filter(student=student).exists():
                                    roll = BTRollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                    roll.save()
                        BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId).exclude(student__RegNo__in=backlog_rolls).delete()
                    elif mode == 'M':
                        makeup_rolls = list(BTStudentMakeups.objects.filter(Dept=dept, BYear=byear, BSem=bsem).values_list('RegNo', flat=True).distinct())
                        makeup_rolls.sort()
                        initial_roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                        BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId).exclude(student__RegNo__in=makeup_rolls).delete()

                        if byear==1:
                            for regd_no in makeup_rolls:
                                student = BTStudentInfo.objects.get(RegNo=regd_no)
                                if not initial_roll_list.filter(student=student, Cycle=dept).exists():
                                        roll = BTRollLists_Staging(RegEventId_id=currentRegEventId, student=student, Cycle=dept)
                                        roll.save()
                        else:
                            for regd_no in makeup_rolls:
                                student = BTStudentInfo.objects.get(RegNo=regd_no)
                                if not initial_roll_list.filter(student=student).exists():
                                        roll = BTRollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                        roll.save()
                    elif mode == 'D':
                        dropped_courses = BTDroppedRegularCourses.objects.filter(subject__RegEventId__BYear=byear, subject__RegEventId__Regulation=regulation)
                        dropped_regno=[]
                        for row in dropped_courses:
                            sub_reg = BTStudentRegistrations_Staging.objects.filter(RegNo=row.student.RegNo, sub_id=row.subject.id)
                            if(len(sub_reg) == 0):
                                dropped_regno.append(row.student)
                        dropped_regno = list(set(dropped_regno))
                        dropped_regno.sort()
                        initial_roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
                        BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId).exclude(student__RegNo__in=dropped_regno).delete()
                        for student in dropped_regno:
                            if not initial_roll_list.filter(student=student).exists():
                                roll = BTRollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                roll.save()
                    return (render(request, 'BTco_ordinator/RollListGenerateSuccess.html'))

    else:
        form = GenerateRollListForm(regIDs)
    return  render(request, 'BTco_ordinator/generateRollList.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def first_year_rollLists_cycle_handler(request):
    not_prom_regs = request.session.get('not_promoted_regno')
    (ayear,asem,byear,bsem,regulation)=request.session.get('ayasbybsr')
    currentRegEventId = request.session.get('currentRegEventId')
    if(request.method == 'POST'):
        form = RollListsCycleHandlerForm(not_prom_regs,request.POST)
        if(form.is_valid()):
            for cIndex, sReg in enumerate(not_prom_regs):
                if(form.cleaned_data.get('RadioMode'+str(sReg))):
                    cycle = form.cleaned_data.get('RadioMode'+str(sReg))
                    s_info = BTStudentInfo.objects.get(RegNo=sReg)
                    if not BTRollLists_Staging.objects.filter(student=s_info, RegEventId_id=currentRegEventId).exists():
                        roll = BTRollLists_Staging(student=s_info, RegEventId_id=currentRegEventId, Cycle=cycle)
                        roll.save()
                    else:
                        BTRollLists_Staging.objects.filter(student=s_info, RegEventId_id=currentRegEventId).update(Cycle=cycle)
                    s_info.Cycle=cycle
                    s_info.save()
            return (render(request, 'BTco_ordinator/RollListGenerateSuccess.html'))
    else:
        form = RollListsCycleHandlerForm(Options=not_prom_regs)
    return (render(request, 'BTco_ordinator/RollListsCycleHandlerForm.html',{'form':form}))



@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def UploadSectionInfo(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if(request.method=='POST'):
        form=UploadSectionInfoForm(regIDs, request.POST,request.FILES)
        if(form.is_valid()):
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            errDataset=Dataset()
            regeventid=form.cleaned_data['regID']
            errData = []
            if(form.cleaned_data['regID']!=''):
                roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=regeventid)
                for row in dataset:
                    if roll_list.filter(id=row[0]).exists():
                        roll=roll_list.filter(id=row[0]).first()
                        roll.Cycle = row[8]
                        roll.Section=row[9]
                        roll.save()
                    else:
                        errData.append(row)
                msg = 'Section Information has been updated successfully.'
                return (render(request, 'BTco_ordinator/SectionUpload.html', {'form':form, 'errorRows':errData, 'msg':msg}))
                  
    else:
        form = UploadSectionInfoForm(regIDs)
    return  render(request, 'BTco_ordinator/SectionUpload.html',{'form':form})




@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def RollList_Status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, BYear=co_ordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1)
    if request.method == 'POST':
        form = RollListStatusForm(regIDs, request.POST)
        if(form.is_valid()):
            if request.POST['regID'] != '--Choose Event--':
                regEvent = form.cleaned_data['regID']
                strs = regEvent.split(':')
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I',2:'II',3:'III',4:'IV'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
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
                rollListStatus=BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId).order_by('student__RegNo')
                if request.POST.get('download'):
                    from BTco_ordinator.utils import RollListBookGenerator
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    response['Content-Disposition'] = 'attachment; filename=RollList({event}).xlsx'.format(event=regEvent)
                    BookGenerator = RollListBookGenerator(rollListStatus, regEvent)
                    workbook = BookGenerator.generate_workbook()
                    workbook.save(response)
                    return response

                return (render(request, 'BTco_ordinator/RollListStatus.html',{'form':form,'rolls': rollListStatus}))            
    form = RollListStatusForm(regIDs)
    return render(request, 'BTco_ordinator/RollListStatus.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def RollListFeeUpload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if(request.method=='POST'):
        form=RollListFeeUploadForm(regIDs, request.POST,request.FILES)
        if(form.is_valid()):
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            regeventid=form.cleaned_data['regID']
            if(form.cleaned_data['regID']!='--Choose Event--'):
                event = BTRegistrationStatus.objects.filter(id=regeventid).first()
                mode = event.Mode
                paid_regd_no = []
                for row in dataset:
                    paid_regd_no.append(row[1])
                rolls = BTRollLists_Staging.objects.filter(RegEventId_id=regeventid)
                unpaid_regd_no = rolls.exclude(student__RegNo__in=paid_regd_no)
                rolls = rolls.values_list('student__RegNo', flat=True)
                error_regd_no = set(paid_regd_no).difference(set(rolls))
                if mode == 'R':
                    for regd_no in unpaid_regd_no:
                        not_registered = BTNotRegistered(Student=regd_no.student, RegEventId_id=regeventid, Registered=False)
                        not_registered.save()
                unpaid_regd_no = unpaid_regd_no.values_list('student__RegNo', flat=True) 
                BTStudentRegistrations_Staging.objects.filter(RegNo__in=unpaid_regd_no, RegEventId=regeventid).delete()
                BTRollLists_Staging.objects.filter(student__RegNo__in=unpaid_regd_no, RegEventId_id=regeventid).delete() 
                currentRegEvent = BTRegistrationStatus.objects.get(id=regeventid)
                currentRegEvent.RollListFeeStatus = 1
                currentRegEvent.save()
                return render(request, 'BTco_ordinator/RollListFeeUploadSuccess.html', {'errors':error_regd_no})      
    else:
        form = RollListFeeUploadForm(regIDs)
    return  render(request, 'BTco_ordinator/RollListFeeUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def NotRegisteredStatus(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='R')
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1, Mode='R')
    if request.method == 'POST':
        form = NotRegisteredStatusForm(regIDs, request.POST)
        if(form.is_valid):
            regEventId=request.POST.get('regID')
            not_regd_status=BTNotRegistered.objects.filter(RegEventId_id=regEventId).order_by('Student__RegNo')
            return (render(request, 'BTco_ordinator/NotRegisteredStatus.html',{'form': form, 'not_regd':not_regd_status}))            
    else:
        form = NotRegisteredStatusForm(regIDs)
    return render(request, 'BTco_ordinator/NotRegisteredStatus.html', {'form':form})



@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def rolllist_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear).exclude(RollListFeeStatus=0)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=cycle_cord.Cycle, BYear=1).exclude(RollListFeeStatus=0)
    if request.method == 'POST':
        form = RollListFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            regEvent = form.cleaned_data['regID']
            rolls = BTRollLists_Staging.objects.filter(RegEventId_id=regEvent)
            for roll in rolls:
                finalized_roll = BTRollLists(student=roll.student, RegEventId=roll.RegEventId, Section=roll.Section, Cycle=roll.Cycle)
                finalized_roll.save()
            reg_status_obj = BTRegistrationStatus.objects.filter(id=regEvent).first()
            reg_status_obj.RollListStatus = 0
            reg_status_obj.save()
            return render(request, 'BTco_ordinator/RollListsFinalize.html', {'form':form, 'success':'Roll List has been successfully finalized.'})
    else:
        form = RollListFinalizeForm(regIDs)
    return render(request, 'BTco_ordinator/RollListsFinalize.html', {'form':form})


