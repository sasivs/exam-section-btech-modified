
from ADAUGDB.models import BTRegistrationStatus
from BTco_ordinator.forms import (GenerateRollListForm,
                                  NotRegisteredStatusForm,
                                  RollListFeeUploadForm, RollListFinalizeForm,
                                  RollListStatusForm,
                                  UploadSectionInfoForm)
from BTco_ordinator.models import (BTDroppedRegularCourses, BTNotPromoted,
                                   BTNotRegistered,
                                   BTRollLists, BTRollLists_Staging,
                                   BTStudentBacklogs, BTStudentMakeups,
                                   BTStudentRegistrations_Staging)
from BTExamStaffDB.models import BTStudentInfo
from BThod.models import BTCoordinator
from ADAUGDB.models import BTHOD, BTCycleCoordinator
from ADAUGDB.user_access_test import (roll_list_access,
                                               roll_list_status_access)
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render
from import_export.formats.base_formats import XLSX
from tablib import Dataset

@transaction.atomic
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
        form = GenerateRollListForm(regIDs, request.POST)
        if(form.is_valid()):
            event = BTRegistrationStatus.objects.get(id=form.cleaned_data.get('regID'))
            BTNotRegistered.objects.filter(RegEventId_id=event.id).delete()
            if event.Mode == 'R':
                if event.BYear == 1:
                    if event.ASem == 1:
                        students = BTStudentInfo.objects.filter(AdmissionYear=event.AYear,Cycle=event.Dept,Regulation=event.Regulation)
                        not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1,BYear=1, PoA_sem1='R', student__Regulation=event.Regulation, student__Cycle=event.Dept)
                        not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                            Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                        
                        initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                        valid_regnos = []
                        for stu_obj in students:
                            if not BTRollLists.objects.filter(student__RegNo=stu_obj.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                        RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=stu_obj.RegNo).exists():
                                    roll = BTRollLists_Staging(student=stu_obj, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(stu_obj.RegNo)
                        
                        for not_prom_obj in not_prom_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                    RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_prom_obj.student.RegNo)
                        
                        for not_reg_obj in not_registered_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                    RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_reg_obj.Student.RegNo)
                        BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()

                    elif event.ASem == 2:
                        previous_sem_event = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=1, BYear=event.BYear, BSem=1, Regulation=event.Regulation, Mode='R', Dept=event.Dept).first()
                        previous_sem_rolllist = BTRollLists_Staging.objects.filter(RegEventId__id=previous_sem_event.id)
                        previous_sem_not_reg_students = BTNotRegistered.objects.filter(RegEventId_id=previous_sem_event.id)

                        not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1,BYear=1, PoA_sem2='R', student__Regulation=event.Regulation, student__Cycle=event.Dept)

                        not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                            Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)

                        initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                        valid_regnos = []

                        for roll in previous_sem_rolllist:
                            if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(roll.student.RegNo)
                            
                        for not_prom_obj in not_prom_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_prom_obj.student.RegNo)

                        for not_reg_obj in not_registered_students|previous_sem_not_reg_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                    RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_reg_obj.Student.RegNo)
                        

                        BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()
                
                else:
                    if event.ASem == 1:
                        if event.BYear == 2:
                            prev_yr_not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear-1, Regulation=event.Regulation)
                            previous_year_rolllist = BTRollLists.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear-1, \
                                RegEventId__Regulation=event.Regulation, RegEventId__Mode=event.Mode, student__Dept=event.Dept).exclude(student__in=prev_yr_not_prom_students.values_list('student', flat=True))
                        else:
                            prev_yr_not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear-1, Regulation=event.Regulation, student__Dept=event.Dept)
                            previous_year_rolllist = BTRollLists.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear-1, \
                                RegEventId__Regulation=event.Regulation, RegEventId__Mode=event.Mode, RegEventId__Dept=event.Dept).exclude(student__in=prev_yr_not_prom_students.values_list('student', flat=True))
                        
                        not_prom_r_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, student__Regulation=event.Regulation, PoA_sem1='R')

                        not_prom_b_students = BTNotPromoted.objects.filter(AYear=event.AYear-2, BYear=event.BYear-1, student__Regulation=event.Regulation, PoA_sem1='B', PoA_sem2='B')

                        not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                            Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                        
                        initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                        valid_regnos = []
                        
                        for roll in previous_year_rolllist:
                            if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                    RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id)
                                    roll.save()
                                valid_regnos.append(roll.student.RegNo)
                        
                        for not_prom_obj in not_prom_r_students|not_prom_b_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_prom_obj.student.RegNo)
                        
                        for not_reg_obj in not_registered_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_reg_obj.Student.RegNo)
                        
                        BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()
                    
                    if event.ASem == 2:
                        previous_sem_event = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=1, BYear=event.BYear, BSem=1, Regulation=event.Regulation, Mode='R', Dept=event.Dept).first()
                        previous_sem_rolllist = BTRollLists.objects.filter(RegEventId_id=previous_sem_event.id)
                        previous_sem_not_reg_students = BTNotRegistered.objects.filter(RegEventId_id=previous_sem_event.id)

                        not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem2='R', student__Regulation=event.Regulation, student__Dept=event.Dept)

                        not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                            Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                        
                        initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                        valid_regnos = []

                        for roll in previous_sem_rolllist:
                            if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(roll.student.RegNo)
                        
                        for not_prom_obj in not_prom_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_prom_obj.student.RegNo)
                        
                        for not_reg_obj in not_registered_students|previous_sem_not_reg_students:
                            if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                                if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                    roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                    roll.save()
                                valid_regnos.append(not_reg_obj.Student.RegNo)
                        
                        BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()

            elif event.Mode == 'B':
                initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)

                backlog_students = BTStudentBacklogs.objects.filter(BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Regulation=event.Regulation).exclude(AYASBYBS__startswith=event.AYear).order_by('RegNo').distinct('RegNo')

                if event.BYear == 1:
                    for student in backlog_students:
                        student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                        if not initial_rolllist.filter(student=student).exists():
                            roll = BTRollLists_Staging(student=student, RegEventId_id=event.id, Cycle=event.Dept)
                            roll.save()
                else:
                    for student in backlog_students:
                        student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                        if not initial_rolllist.filter(student=student).exists():
                            roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                            roll.save()
                        
                BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__RegNo__in=backlog_students.values_list('RegNo', flat=True)).delete()

            elif event.Mode == 'M':
                initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                
                makeup_students = BTStudentMakeups.objects.filter(Dept=event.Dept, BYear=event.BYear, BSem=event.BSem, Regulation=event.Regulation).distinct('RegNo').order_by('RegNo')

                if event.BYear == 1:
                    for student in makeup_students:
                        student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                        if not initial_rolllist.filter(student=student).exists():
                            roll = BTRollLists_Staging(student=student, RegEventId_id=event.id, Cycle=event.Dept)
                            roll.save()
                else:
                    for student in makeup_students:
                        student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                        if not initial_rolllist.filter(student=student).exists():
                            roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                            roll.save()
                
                BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__RegNo__in=makeup_students.values_list('RegNo', flat=True)).delete()

            elif event.Mode == 'D':
                initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)

                dropped_courses_students = BTDroppedRegularCourses.objects.filter(Registered=False, subject_RegEventId__BYear=event.BYear, subject__RegEventId__Regulation=event.Regulation).\
                    exclude(subject__RegEventId__AYear=event.AYear).distinct('student__RegNo').order_by('student__RegNo')

                for student in dropped_courses_students:
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                        roll.save()
            return render(request, 'BTco_ordinator/RollListGenerateSuccess.html')
    else:
        form = GenerateRollListForm(regIDs)
    return  render(request, 'BTco_ordinator/generateRollList.html',{'form':form})  

# @login_required(login_url="/login/")
# @user_passes_test(roll_list_access)
# def first_year_rollLists_cycle_handler(request):
#     not_prom_regs = request.session.get('not_promoted_regno')
#     (ayear,asem,byear,bsem,regulation)=request.session.get('ayasbybsr')
#     currentRegEventId = request.session.get('currentRegEventId')
#     if(request.method == 'POST'):
#         form = RollListsCycleHandlerForm(not_prom_regs,request.POST)
#         if(form.is_valid()):
#             for cIndex, sReg in enumerate(not_prom_regs):
#                 if(form.cleaned_data.get('RadioMode'+str(sReg))):
#                     cycle = form.cleaned_data.get('RadioMode'+str(sReg))
#                     s_info = BTStudentInfo.objects.get(RegNo=sReg)
#                     if not BTRollLists_Staging.objects.filter(student=s_info, RegEventId_id=currentRegEventId).exists():
#                         roll = BTRollLists_Staging(student=s_info, RegEventId_id=currentRegEventId, Cycle=cycle)
#                         roll.save()
#                     else:
#                         BTRollLists_Staging.objects.filter(student=s_info, RegEventId_id=currentRegEventId).update(Cycle=cycle)
#                     s_info.Cycle=cycle
#                     s_info.save()
#             return (render(request, 'BTco_ordinator/RollListGenerateSuccess.html'))
#     else:
#         form = RollListsCycleHandlerForm(Options=not_prom_regs)
#     return (render(request, 'BTco_ordinator/RollListsCycleHandlerForm.html',{'form':form}))


@transaction.atomic
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
            regeventid=form.cleaned_data['regID']
            errData = []
            if(form.cleaned_data['regID']!=''):
                roll_list = BTRollLists_Staging.objects.filter(RegEventId_id=regeventid)
                for row in dataset:
                    if roll_list.filter(id=row[0]).exists():
                        roll=roll_list.filter(id=row[0]).first()
                        roll.Cycle = row[5]
                        roll.Section=row[6]
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
    if 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
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
            currentRegEvent = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
            rollListStatus=BTRollLists_Staging.objects.filter(RegEventId_id=currentRegEvent.id).order_by('student__RegNo')
            if request.POST.get('download'):
                from BTco_ordinator.utils import RollListBookGenerator
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                response['Content-Disposition'] = 'attachment; filename=RollList({event}).xlsx'.format(event=currentRegEvent.__str__())
                BookGenerator = RollListBookGenerator(rollListStatus, currentRegEvent)
                workbook = BookGenerator.generate_workbook()
                workbook.save(response)
                return response
            return (render(request, 'BTco_ordinator/RollListStatus.html',{'form':form,'rolls': rollListStatus}))            
    form = RollListStatusForm(regIDs)
    return render(request, 'BTco_ordinator/RollListStatus.html', {'form':form})

@transaction.atomic
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
                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo__in=unpaid_regd_no, RegEventId=regeventid).delete()
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
    if 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
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


@transaction.atomic
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
                if(not BTRollLists.objects.filter(student=roll.student, RegEventId=roll.RegEventId).exists()):
                    finalized_roll = BTRollLists(student=roll.student, RegEventId=roll.RegEventId, Section=roll.Section, Cycle=roll.Cycle)
                    finalized_roll.save()
            reg_status_obj = BTRegistrationStatus.objects.filter(id=regEvent).first()
            reg_status_obj.RollListStatus = 0
            reg_status_obj.save()
            return render(request, 'BTco_ordinator/RollListsFinalize.html', {'form':form, 'success':'Roll List has been successfully finalized.'})
    else:
        form = RollListFinalizeForm(regIDs)
    return render(request, 'BTco_ordinator/RollListsFinalize.html', {'form':form})


def roll_list_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    for event in events:
        BTNotRegistered.objects.filter(RegEventId_id=event.id).delete()
        if event.Mode == 'R':
            if event.BYear == 1:
                if event.ASem == 1:
                    students = BTStudentInfo.objects.filter(AdmissionYear=event.AYear,Cycle=event.Dept,Regulation=event.Regulation)
                    not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1,BYear=1, PoA_sem1='R', student__Regulation=event.Regulation, student__Cycle=event.Dept)
                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                    
                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []
                    for stu_obj in students:
                        if not BTRollLists.objects.filter(student__RegNo=stu_obj.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                    RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=stu_obj.RegNo).exists():
                                roll = BTRollLists_Staging(student=stu_obj, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(stu_obj.RegNo)
                    
                    for not_prom_obj in not_prom_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)
                    
                    for not_reg_obj in not_registered_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()

                elif event.ASem == 2:
                    previous_sem_event = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=1, BYear=event.BYear, BSem=1, Regulation=event.Regulation, Mode='R', Dept=event.Dept).first()
                    previous_sem_rolllist = BTRollLists_Staging.objects.filter(RegEventId__id=previous_sem_event.id)
                    previous_sem_not_reg_students = BTNotRegistered.objects.filter(RegEventId_id=previous_sem_event.id)

                    not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1,BYear=1, PoA_sem2='R', student__Regulation=event.Regulation, student__Cycle=event.Dept)

                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)

                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []

                    for roll in previous_sem_rolllist:
                        if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(roll.student.RegNo)
                        
                    for not_prom_obj in not_prom_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)

                    for not_reg_obj in not_registered_students|previous_sem_not_reg_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    

                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()
            
            else:
                if event.ASem == 1:
                    if event.BYear == 2:
                        prev_yr_not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear-1, Regulation=event.Regulation)
                        previous_year_rolllist = BTRollLists.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear-1, \
                            RegEventId__Regulation=event.Regulation, RegEventId__Mode=event.Mode, student__Dept=event.Dept).exclude(student__in=prev_yr_not_prom_students.values_list('student', flat=True))
                    else:
                        prev_yr_not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear-1, Regulation=event.Regulation, student__Dept=event.Dept)
                        previous_year_rolllist = BTRollLists.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear-1, \
                            RegEventId__Regulation=event.Regulation, RegEventId__Mode=event.Mode, RegEventId__Dept=event.Dept).exclude(student__in=prev_yr_not_prom_students.values_list('student', flat=True))
                    
                    not_prom_r_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, student__Regulation=event.Regulation, PoA_sem1='R')

                    not_prom_b_students = BTNotPromoted.objects.filter(AYear=event.AYear-2, BYear=event.BYear-1, student__Regulation=event.Regulation, PoA_sem1='B', PoA_sem2='B')

                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                    
                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []
                    
                    for roll in previous_year_rolllist:
                        if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id)
                                roll.save()
                            valid_regnos.append(roll.student.RegNo)
                    
                    for not_prom_obj in not_prom_r_students|not_prom_b_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)
                    
                    for not_reg_obj in not_registered_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    
                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()
                
                if event.ASem == 2:
                    previous_sem_event = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=1, BYear=event.BYear, BSem=1, Regulation=event.Regulation, Mode='R', Dept=event.Dept).first()
                    previous_sem_rolllist = BTRollLists.objects.filter(RegEventId_id=previous_sem_event.id)
                    previous_sem_not_reg_students = BTNotRegistered.objects.filter(RegEventId_id=previous_sem_event.id)

                    not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem2='R', student__Regulation=event.Regulation, student__Dept=event.Dept)

                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                    
                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []

                    for roll in previous_sem_rolllist:
                        if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(roll.student.RegNo)
                    
                    for not_prom_obj in not_prom_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)
                    
                    for not_reg_obj in not_registered_students|previous_sem_not_reg_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    
                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()

        elif event.Mode == 'B':
            initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)

            backlog_students = BTStudentBacklogs.objects.filter(BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Regulation=event.Regulation).exclude(AYASBYBS__startswith=event.AYear).order_by('RegNo').distinct('RegNo')

            if event.BYear == 1:
                for student in backlog_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id, Cycle=event.Dept)
                        roll.save()
            else:
                for student in backlog_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                        roll.save()
                    
            BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__RegNo__in=backlog_students.values_list('RegNo', flat=True)).delete()

        elif event.Mode == 'M':
            initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
            
            makeup_students = BTStudentMakeups.objects.filter(Dept=event.Dept, BYear=event.BYear, BSem=event.BSem, Regulation=event.Regulation).distinct('RegNo').order_by('RegNo')

            if event.BYear == 1:
                for student in makeup_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id, Cycle=event.Dept)
                        roll.save()
            else:
                for student in makeup_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                        roll.save()
            
            BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__RegNo__in=makeup_students.values_list('RegNo', flat=True)).delete()

        elif event.Mode == 'D':
            initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)

            dropped_courses_students = BTDroppedRegularCourses.objects.filter(Registered=False, subject_RegEventId__BYear=event.BYear, subject__RegEventId__Regulation=event.Regulation).\
                exclude(subject__RegEventId__AYear=event.AYear).distinct('student__RegNo').order_by('student__RegNo')

            for student in dropped_courses_students:
                if not initial_rolllist.filter(student=student).exists():
                    roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                    roll.save()

def rollList_fee_upload_script(file, kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    file = open(file)
    data = bytes()
    for chunk in file.chunks():
        data += chunk
    dataset = XLSX().create_dataset(data)
    event = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), ASem=kwargs.get('ASem'), BYear=kwargs.get('BYear'), BSem=kwargs.get('BSem'),\
        Regulation=kwargs.get('Regulation'), Dept=kwargs.get('Dept'), Mode=kwargs.get('Mode')).first()
    mode = event.Mode
    paid_regd_no = []
    for row in dataset:
        paid_regd_no.append(row[1])
    rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
    unpaid_regd_no = rolls.exclude(student__RegNo__in=paid_regd_no)
    rolls = rolls.values_list('student__RegNo', flat=True)
    error_regd_no = set(paid_regd_no).difference(set(rolls))
    if mode == 'R':
        for regd_no in unpaid_regd_no:
            not_registered = BTNotRegistered(Student=regd_no.student, RegEventId_id=event.id, Registered=False)
            not_registered.save()
    unpaid_regd_no = unpaid_regd_no.values_list('student__RegNo', flat=True) 
    BTStudentRegistrations_Staging.objects.filter(student__student__RegNo__in=unpaid_regd_no, RegEventId=event.id).delete()
    BTRollLists_Staging.objects.filter(student__RegNo__in=unpaid_regd_no, RegEventId_id=event.id).delete() 
    currentRegEvent = BTRegistrationStatus.objects.get(id=event.id)
    currentRegEvent.RollListFeeStatus = 1
    currentRegEvent.save()
    print(error_regd_no)
    print('These roll numbers are not there in roll list')
    return "Done!"

def rolls_finalize_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    for event in events:
        rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
        for roll in rolls:
            if(not BTRollLists.objects.filter(student=roll.student, RegEventId=roll.RegEventId).exists()):
                finalized_roll = BTRollLists(student=roll.student, RegEventId=roll.RegEventId, Section=roll.Section, Cycle=roll.Cycle)
                finalized_roll.save()
        event.RollListStatus = 0
        event.save()
    return "Done! "

def rollList_download_script(event):
    from BTco_ordinator.utils import RollListBookGenerator
    rollListStatus=BTRollLists_Staging.objects.filter(RegEventId_id=event.id).order_by('student__RegNo')
    BookGenerator = RollListBookGenerator(rollListStatus, event)
    workbook = BookGenerator.generate_workbook()
    filename = 'RollList({event}).xlsx'.format(event=event.__str__())
    workbook.save()
    return "Done!!"