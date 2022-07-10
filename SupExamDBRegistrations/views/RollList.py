
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.urls import reverse
from django.db.models import Q

from SupExamDBRegistrations.forms import RollListStatusForm, RollListRegulationDifferenceForm,\
     RollListFinalizeForm, GenerateRollListForm, RollListsCycleHandlerForm, RollListStatusForm, UpdateSectionInfoForm, UploadSectionInfoForm,\
        RollListFeeUploadForm, NotRegisteredStatusForm
from SupExamDBRegistrations.models import Regulation, RegulationChange, RollLists_Staging, StudentInfo, NotPromoted, RollLists,\
    RegistrationStatus,StudentRegistrations_Staging, StudentBacklogs, StudentMakeups, DroppedRegularCourses, NotRegistered
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from SupExamDBRegistrations.user_access_test import roll_list_access

@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def generateRollList(request):
    if request.method == 'POST':
        if 'Regulation_change' in request.POST:
            (ayear,asem,byear,bsem,regulation)=request.session.get('ayasbybsr')
            print(ayear,asem,byear,bsem,regulation)
            if(byear ==1):
                not_promoted_regno = request.session.get('not_promoted_regno_firstyear')  
            else:
                not_promoted_regno = request.session.get('not_promoted_regno')
                
            
            not_promoted_regnos =[]
            ayasbybsr = (ayear,asem,byear,bsem,regulation)
            form = RollListRegulationDifferenceForm((not_promoted_regno,regulation),request.POST)
           
            if(form.is_valid()):
        
                for cIndex, sReg in enumerate(not_promoted_regno):
                    print(cIndex,sReg)
                    if(form.cleaned_data.get('RadioMode'+str(sReg))):
                        choice = form.cleaned_data.get('RadioMode'+str(sReg))
                        
                        s_info = StudentInfo.objects.get(RegNo=sReg)
                        if(choice == 'YES'):
                            if(byear ==1):
                                not_promoted_regnos.append(sReg)
                            else:
                                roll = RollLists_Staging.objects.filter(student=s_info, RegEventId_id=request.session.get('currentRegEventId'))
                                if(len(roll) == 0):
                                    roll = RollLists_Staging(student=s_info, RegEventId_id=request.session.get('currentRegEventId'))
                                    roll.save()
                            prev_regulation  = s_info.Regulation
                            s_info.Regulation = regulation
                            s_info.save()
                            if(prev_regulation != regulation):
                                currentRegEventId = request.session.get('currentRegEventId')
                                regu_change = RegulationChange(RegEventId = currentRegEventId, student= s_info, \
                                    PreviousRegulation=prev_regulation ,PresentRegulation=regulation)
                                regu_change.save()
                        else:
                            RollLists_Staging.objects.filter(student__RegNo=sReg, RegEventId_id=request.session.get('currentRegEventId')).delete()
                
                if(len(not_promoted_regnos)!=0 and byear ==1 ):
                        request.session['not_promoted_regno'] = (not_promoted_regnos)
                        request.session['ayasbybsr'] = ayasbybsr
                        request.session['currentRegEventId'] = request.session.get('currentRegEventId')
                        return HttpResponseRedirect(reverse('FirstYearRollListsCycleHandler' ))
                return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html')) 
            
        else:
            form = GenerateRollListForm(request.POST)
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
                    currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation)
                    currentRegEventId = currentRegEventId[0].id
                    if mode == 'R':
                        if(byear==1):
                            reg_rgs = StudentInfo.objects.filter(AdmissionYear=ayear,Cycle=dept,Regulation=regulation)
                            not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=1, Regulation=regulation, PoA='R', student__Cycle=dept)
                            regular_regd_no = list(reg_rgs.values_list('RegNo', flat=True))
                            not_prom_regs = [row.student.RegNo for row in not_prom_regs]

                            valid_rolls = regular_regd_no+not_prom_regs

                            initial_roll_list = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                            RollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_rolls), RegEventId_id=currentRegEventId).delete()


                            for row in reg_rgs:
                                if not initial_roll_list.filter(student=row, Cycle=row.Cycle).exists():
                                    roll = RollLists_Staging(student=row, Cycle=row.Cycle, RegEventId_id=currentRegEventId)
                                    roll.save()
                        
                            if(len( not_prom_regs) !=0):
                                regulation_form = RollListRegulationDifferenceForm(Options = (not_prom_regs,regulation))
                                request.session['not_promoted_regno_firstyear'] = not_prom_regs
                                request.session['ayasbybsr'] = ayasbybsr
                                request.session['currentRegEventId'] = currentRegEventId
                                return render(request, 'SupExamDBRegistrations/generateRollList.html',{'form':form, 'regulation_form':regulation_form})
                            return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))

                                
                        else:
                            if byear==2:
                                prev_regEventId = RegistrationStatus.objects.filter(AYear=ayear-1, BYear=byear-1, Regulation=regulation, Mode=mode)
                            else:
                                prev_regEventId = RegistrationStatus.objects.filter(AYear=ayear-1, BYear=byear-1, Regulation=regulation, Mode=mode, Dept=dept)  
                            present_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=byear)
                            not_promoted_bmode = NotPromoted.objects.filter(AYear=ayear-2, BYear=byear-1, PoA='B')
                            not_promoted_regs = present_not_prom_regs | not_promoted_bmode
                            prev_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1, BYear=byear-1)
                            prev_not_prom_regd_no = prev_not_prom_regs.values_list('student__RegNo', flat=True)
                            prev_not_prom_regs = prev_not_prom_regs.values_list('student', flat=True)
                            reg_rgs = RollLists_Staging.objects.filter(~Q(student__in=prev_not_prom_regs), RegEventId_id__in=prev_regEventId, student__Dept=dept)
                            not_promoted_regno=[row.student.RegNo for row in not_promoted_regs]

                            regular_regd_no = reg_rgs.values_list('student__RegNo', flat=True)
                            valid_rolls = regular_regd_no + not_promoted_regno
                            
                            initial_roll_list = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                            RollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_rolls), RegEventId_id=currentRegEventId).delete()


                            for reg in reg_rgs:
                                if not initial_roll_list.filter(student=reg.student).exists():
                                    roll = RollLists_Staging(student=reg.student, RegEventId_id=currentRegEventId)
                                    roll.save()
                            
                            StudentRegistrations_Staging.objects.filter(RegNo__in=prev_not_prom_regd_no,RegEventId=currentRegEventId).delete()
                            RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId, student__in=prev_not_prom_regs).delete()

                            
                            if(len(not_promoted_regno) != 0):
                                request.session['not_promoted_regno'] = not_promoted_regno
                                request.session['ayasbybsr'] = ayasbybsr
                                request.session['currentRegEventId'] = currentRegEventId
                                regulation_form = RollListRegulationDifferenceForm(Options = (not_promoted_regno,regulation))
                                return render(request, 'SupExamDBRegistrations/generateRollList.html',{'form':form,'regulation_form':regulation_form })

                    elif mode == 'B':

                        initial_roll_list = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                        RollLists_Staging.objects.exclude(RegEventId_id=currentRegEventId, student__RegNo__in=backlog_rolls).delete()
                        if byear == 1:

                            backlog_rolls = StudentBacklogs.objects.filter(BYear=byear, Dept=dept).values_list('RegNo', flat=True)
                            backlog_rolls = list(set(backlog_rolls))
                            backlog_rolls.sort()

                            for regd_no in backlog_rolls:
                                student = StudentInfo.objects.get(RegNo=regd_no)
                                if not initial_roll_list.filter(student=student, Cycle=dept).exists():
                                    roll = RollLists_Staging(RegEventId_id=currentRegEventId, student=student, Cycle=dept)
                                    roll.save()
                        else:

                            backlog_rolls = StudentBacklogs.objects.filter(BYear=byear, Dept=dept, BSem=bsem).values_list('RegNo', flat=True)
                            backlog_rolls = list(set(backlog_rolls))
                            backlog_rolls.sort()

                            for regd_no in backlog_rolls:
                                student = StudentInfo.objects.get(RegNo=regd_no) 
                                if not initial_roll_list.filter(student=student).exists():
                                    roll = RollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                    roll.save()
                    elif mode == 'M':
                        makeup_rolls = list(StudentMakeups.objects.filter(Dept=dept, BYear=byear, BSem=bsem).values_list('RegNo', flat=True).distinct())
                        makeup_rolls.sort()
                        initial_roll_list = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                        RollLists_Staging.objects.exclude(RegEventId_id=currentRegEventId, student__RegNo__in=makeup_rolls)

                        if byear==1:
                            for regd_no in makeup_rolls:
                                student = StudentInfo.objects.get(RegNo=regd_no)
                                if not initial_roll_list.filter(student=student, Cycle=dept).exists():
                                        roll = RollLists_Staging(RegEventId_id=currentRegEventId, student=student, Cycle=dept)
                                        roll.save()
                        else:
                            for regd_no in makeup_rolls:
                                student = StudentInfo.objects.get(RegNo=regd_no)
                                if not initial_roll_list.filter(student=student).exists():
                                        roll = RollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                        roll.save()
                    elif mode == 'D':
                        dropped_courses = DroppedRegularCourses.objects.filter(subject__RegEventId__BYear=byear, subject__RegEventId__Regulation=regulation)
                        dropped_regno=[]
                        for row in dropped_courses:
                            sub_reg = StudentRegistrations_Staging.objects.filter(RegNo=row.student.RegNo, sub_id=row.subject.id)
                            if(len(sub_reg) == 0):
                                dropped_regno.append(row.student)
                        dropped_regno = list(set(dropped_regno))
                        dropped_regno.sort()
                        initial_roll_list = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
                        RollLists_Staging.objects.exclude(student__RegNo__in=dropped_regno, RegEventId_id=currentRegEventId).delete()
                        for student in dropped_regno:
                            if not initial_roll_list.filter(student=student).exists():
                                roll = RollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                roll.save()
                    return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))

    else:
        form = GenerateRollListForm()
    return  render(request, 'SupExamDBRegistrations/generateRollList.html',{'form':form})

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
                    s_info = StudentInfo.objects.get(RegNo=sReg)
                    roll = RollLists_Staging(student=s_info, RegEventId_id=currentRegEventId, Cycle=cycle)
                    s_info.Cycle=cycle
                    s_info.save()
                    roll.save()
        return (render(request, 'SupExamDBRegistrations/RollListGenerateSuccess.html'))
    else:
        form = RollListsCycleHandlerForm(Options=not_prom_regs)
    return (render(request, 'SupExamDBRegistrations/RollListsCycleHandlerForm.html',{'form':form}))





# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def RollList_Status(request):
#     if request.method == 'POST':
#         form = RollListStatusForm([],request.POST)
#         if(form.is_valid):
#             ayear=int(request.POST.get('aYear'))
#             byear=int(request.POST.get('bYear'))
#             dept=int(request.POST.get('dept'))
#             print(ayear, byear, dept)
#             if(byear==1):
#                 total_regs =[]
#                 reg_rgs = StudentInfo.objects.filter(AdmissionYear=ayear,Cycle=dept)
#                 reg_rgs = [row.RegNo for row in reg_rgs]
#                 total_regs += reg_rgs
#                 not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=1, PoA='R')

#                 not_prom_regs = [row.RegNo for row in not_prom_regs]
                    
#                 final_not_prom_regs = []
                       
#                 for reg in not_prom_regs:
#                     s_info = StudentInfo.objects.get(RegNo=reg)
#                     if(s_info.Cycle==dept):
#                             final_not_prom_regs.append(reg)   
#                 not_prom_regs = final_not_prom_regs
#                 if(len( not_prom_regs) !=0):
#                     total_regs += not_prom_regs
#                 Option =[]
#                 for reg in total_regs:
#                     roll = RollLists_Staging.objects.filter(RegNo=reg,AYear=ayear,BYear=byear)
#                     if(len(roll)!=0):
#                         Option.append((reg,roll[0].AYear,roll[0].BYear,roll[0].Regulation))
#                     else:
#                         Option =[(reg,'','','')] + Option
#                 form = RollListStatusForm(Option,request.POST )
#                 return (render(request, 'SupExamDBRegistrations/RollListStatus.html',{'form': form}))            
#             else:
#                         total_regs =[]
#                         reg_rgs = RollLists_Staging.objects.filter(AYear=ayear-1,Dept=dept,BYear=byear-1)
#                         reg_rgs = [row.RegNo for row in reg_rgs]
#                         pres_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1,BYear=byear)
#                         present_not_prom_regs=[]
#                         not_promoted_regno=[]
#                         for reg in pres_not_prom_regs:
#                             not_promoted_regno.append(reg.RegNo)

#                         present_not_prom_regs = [row.RegNo for row in present_not_prom_regs]
#                         prev_not_prom_regs = NotPromoted.objects.filter(AYear=ayear-1, BYear=byear-1)
#                         prev_not_prom_regs = [row.RegNo for row in prev_not_prom_regs]
#                         final_regs = []
#                         not_prom_prev_prev_bmode = NotPromoted.objects.filter(AYear = ayear-2, BYear= 1, PoA='B')
#                         not_prom_prev_prev_bmode = [row.RegNo for row in not_prom_prev_prev_bmode]
#                         not_promoted_prev_bmode =  NotPromoted.objects.filter(AYear = ayear-1, BYear= 1, PoA='B')
#                         not_promoted_prev_bmode = [row.RegNo for row in not_promoted_prev_bmode]
#                         for reg in not_prom_prev_prev_bmode:
#                             if(reg not in  not_promoted_prev_bmode):
#                                 not_promoted_regno.append(reg)
                            
#                         for reg in reg_rgs:
#                             if(reg not in prev_not_prom_regs):
#                                 final_regs.append(reg)
#                         total_regs += final_regs
#                         print(total_regs) 
#                         total_regs += not_promoted_regno
#                         print(total_regs)
#                         Option =[]
#                         for reg in total_regs:
#                             roll = RollLists_Staging.objects.filter(RegNo=reg,AYear=ayear,BYear=byear)
#                             if(len(roll)!=0):
#                                 Option.append((reg,roll[0].AYear,roll[0].BYear,roll[0].Regulation))
#                             else:
#                                 Option =[(reg,'','','')] + Option
#                         form = RollListStatusForm(Option,request.POST)
#                         return (render(request, 'SupExamDBRegistrations/RollListStatus.html',{'form': form}))            
#     else:
#         Option=[]
#         form = RollListStatusForm(Options=Option)
#         return render(request, 'SupexamDBRegistrations/RollListStatus.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def UploadSectionInfo(request):
    if(request.method=='POST'):
        form=UploadSectionInfoForm( request.POST,request.FILES)
        if(form.is_valid()):
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            errDataset=Dataset()
            regeventid=form.cleaned_data['regID']
            errDataset.headers=['id','RegNo','Cycle','Section']
            errData = []
            if(form.cleaned_data['regID']!='--Choose Event--'):
                for row in dataset:
                    if RollLists_Staging.objects.filter(id=row[0]).exists():
                        roll=RollLists_Staging.objects.get(id=row[0])
                        roll.Cycle = row[8]
                        roll.Section=row[9]
                        roll.save()
                    else:
                        errDataset.append(row)
                for i in errDataset:
                    errData.append(i)
                if(len(errData)!=0):
                    SecInfoErrRows = [ (errData[i][0],errData[i][1],errData[i][8],errData[i][9] ) for i in range(len(errData))]
                    request.session['SecInfoErrRows'] = SecInfoErrRows
                    return HttpResponseRedirect(reverse('UploadSectionInfoErrorHandler'))
                return (render(request, 'SupExamDBRegistrations/SectionInfoUploadSuccess.html'))
                  
    else:
        form = UploadSectionInfoForm()
    return  render(request, 'SupExamDBRegistrations/SectionUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def UploadSectionInfoErrorHandler(request):
    SectionInfoRows = request.session.get('SecInfoErrRows')
    for row in SectionInfoRows:
        print(row[0])
    if(request.method=='POST'):
        form = UpdateSectionInfoForm(SectionInfoRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(SectionInfoRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    RollLists_Staging.objects.filter(id=fRow[0]).update(\
                        regEventId=fRow[1],RegNo=fRow[2],Cycle=fRow[3],Section=fRow[4])
            return render(request, 'SupExamDBRegistrations/SectionInfoUploadSuccess.html')
    else:
        form = UpdateSectionInfoForm(Options=SectionInfoRows)
    return(render(request, 'SupExamDBRegistrations/SectionInfoUploadErrorHandler.html',{'form':form}))



@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def RollList_Status(request):
    if request.method == 'POST':
        form = RollListStatusForm(request.POST)
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
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                rollListStatus=RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
                if request.POST.get('download'):
                    from SupExamDBRegistrations.utils import RollListBookGenerator
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    response['Content-Disposition'] = 'attachment; filename=RollList({event}).xlsx'.format(event=regEvent)
                    BookGenerator = RollListBookGenerator(rollListStatus, regEvent)
                    workbook = BookGenerator.generate_workbook()
                    workbook.save(response)
                    return response

                return (render(request, 'SupExamDBRegistrations/RollListStatus.html',{'form':form,'rolls': rollListStatus}))            
    form = RollListStatusForm()
    return render(request, 'SupexamDBRegistrations/RollListStatus.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def RollListFeeUpload(request):
    if(request.method=='POST'):
        form=RollListFeeUploadForm( request.POST,request.FILES)
        if(form.is_valid()):
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            regeventid=form.cleaned_data['regID']
            if(form.cleaned_data['regID']!='--Choose Event--'):
                paid_regd_no = []
                for row in dataset:
                    paid_regd_no.append(row[1])
                rolls = RollLists_Staging.objects.filter(RegEventId_id=regeventid)
                unpaid_regd_no = rolls.exclude(student__RegNo__in=paid_regd_no)
                rolls = rolls.values_list('student__RegNo', flat=True)
                error_regd_no = set(paid_regd_no).difference(set(rolls))
                for regd_no in unpaid_regd_no:
                    not_registered = NotRegistered(student=regd_no.student, RegEventId_id=regeventid, Registered=False)
                    not_registered.save()
                unpaid_regd_no = unpaid_regd_no.values_list('student__RegNo', flat=True) 
                StudentRegistrations_Staging.objects.filter(RegNo__in=unpaid_regd_no, RegEventId=regeventid).delete()
                RollLists_Staging.objects.filter(student__RegNo__in=unpaid_regd_no, RegEventId_id=regeventid).delete() 
                return render(request, 'SupExamDBRegistrations/RollListFeeUploadSuccess.html', {'errors':error_regd_no})      
    else:
        form = RollListFeeUploadForm()
    return  render(request, 'SupExamDBRegistrations/RollListFeeUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def NotRegisteredStatus(request):
    if request.method == 'POST':
        form = NotRegisteredStatusForm(request.POST)
        if(form.is_valid):
            regEventId=request.POST.get('regID')
            not_regd_status=NotRegistered.objects.filter(RegEventId_id=regEventId) 
            return (render(request, 'SupExamDBRegistrations/NotRegisteredStatus.html',{'form': form, 'not_regd':not_regd_status}))            
    else:
        form = NotRegisteredStatusForm()
        return render(request, 'SupexamDBRegistrations/NotRegisteredStatus.html', {'form':form})



@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def rolllist_finalize(request):
    if request.method == 'POST':
        form = RollListFinalizeForm(request.POST)
        if form.is_valid():
            regEvent = form.cleaned_data['regID']
            rolls = RollLists_Staging.objects.filter(RegEventId_id=regEvent)
            for roll in rolls:
                finalized_roll = RollLists(student=roll.student, RegEventId=roll.RegEventId, Section=roll.Section, Cycle=roll.Cycle)
                finalized_roll.save()
            return render(request, 'SupExamDBRegistrations/RollListsFinalize.html', {'form':form, 'success':'Roll List has been successfully finalized.'})
    form = RollListFinalizeForm()
    return render(request, 'SupExamDBRegistrations/RollListsFinalize.html', {'form':form})








# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def rolllist_finalize_error_handler(request):
    
#     if request.method == 'POST':
#         form = RollListErrorHandlerForm(errRolls, request.POST)
#         if form.is_valid():
#             for i in len(errRolls):
#                 if form.cleaned_data['Check'+str(errRolls[i])]:
#                     addRoll = RollLists(RegNo=errRolls[i])