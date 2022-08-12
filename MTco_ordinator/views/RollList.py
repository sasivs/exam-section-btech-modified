
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q

from MTco_ordinator.forms import RollListStatusForm,RollListFinalizeForm, GenerateRollListForm,  RollListStatusForm,\
        RollListFeeUploadForm, NotRegisteredStatusForm
from MTco_ordinator.models import MTRollLists_Staging, MTRollLists, MTRollLists_Staging, MTRegulationChange, MTStudentBacklogs, MTNotRegistered
from MTsuperintendent.models import MTHOD
from ADPGDB.models import MTRegistrationStatus
from MTExamStaffDB.models import MTStudentInfo 
from MThod.models import MTCoordinator
from MTco_ordinator.models import MTStudentRegistrations_Staging,  MTStudentMakeups
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from MTsuperintendent.user_access_test import roll_list_access, roll_list_status_access

@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def generateRollList(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear)
    if request.method == 'POST':
        form = GenerateRollListForm(regIDs, request.POST)
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
                myear = rom2int[strs[1]]
                msem = rom2int[strs[2]]
                regulation = int(strs[5])
                ayasbybsr = (ayear,asem,myear,msem,regulation)
                mode = strs[6]
                currentRegEvent = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation).first()
                currentRegEventId = currentRegEvent.id
                if mode == 'R':
                    if(myear==1):
                        reg_rgs = MTStudentInfo.objects.filter(AdmissionYear=ayear,Dept=dept,Regulation=regulation)

                        initial_roll_list = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                        MTRollLists_Staging.objects.filter(~Q(student__RegNo__in=reg_rgs.values_list('RegNo', flat=True)), RegEventId_id=currentRegEventId).delete()


                        for row in reg_rgs:
                            if not initial_roll_list.filter(student=row, RegEventId__Dept=row.Dept).exists():
                                roll = MTRollLists_Staging(student=row, RegEventId_id=currentRegEventId)
                                roll.save()
                            
                    else:
                        if myear==2:
                            prev_regEventId = MTRegistrationStatus.objects.filter(AYear=ayear-1, MYear=myear-1, Regulation=regulation, Mode=mode, Dept=dept)
            
                        reg_rgs = MTRollLists_Staging.objects.filter(RegEventId_id__in=prev_regEventId)

                        
                        initial_roll_list = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                        MTRollLists_Staging.objects.filter(~Q(student__RegNo__in=reg_rgs.values_list('student__RegNo', flat=True)), RegEventId_id=currentRegEventId).delete()


                        for reg in reg_rgs:
                            if not initial_roll_list.filter(student=reg.student).exists():
                                roll = MTRollLists_Staging(student=reg.student, RegEventId_id=currentRegEventId)
                                roll.save()

                elif mode == 'B':

                    initial_roll_list = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                    backlog_rolls = MTStudentBacklogs.objects.filter(MYear=myear, Dept=dept, MSem=msem).values_list('RegNo', flat=True)
                    backlog_rolls = list(set(backlog_rolls))
                    backlog_rolls.sort()

                    for regd_no in backlog_rolls:
                        student = MTStudentInfo.objects.get(RegNo=regd_no) 
                        if not initial_roll_list.filter(student=student).exists():
                            roll = MTRollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                            roll.save()
                    MTRollLists_Staging.objects.exclude(RegEventId_id=currentRegEventId, student__RegNo__in=backlog_rolls).delete()
                elif mode == 'M':
                    makeup_rolls = list(MTStudentMakeups.objects.filter(Dept=dept, MYear=myear, MSem=msem).values_list('RegNo', flat=True).distinct())
                    makeup_rolls.sort()
                    initial_roll_list = MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)

                    MTRollLists_Staging.objects.exclude(RegEventId_id=currentRegEventId, student__RegNo__in=makeup_rolls).delete()
                    for regd_no in makeup_rolls:
                        student = MTStudentInfo.objects.get(RegNo=regd_no)
                        if not initial_roll_list.filter(student=student).exists():
                                roll = MTRollLists_Staging(RegEventId_id=currentRegEventId, student=student)
                                roll.save()
                MTNotRegistered.objects.filter(RegEventId_id=currentRegEventId).delete()
                currentRegEvent.RollListFeeStatus = 0
                currentRegEvent.save()
                return (render(request, 'MTco_ordinator/RollListGenerateSuccess.html'))

    else:
        form = GenerateRollListForm(regIDs)
    return  render(request, 'MTco_ordinator/generateRollList.html',{'form':form})



@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def RollListFeeUpload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear)
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
                paid_regd_no = []
                for row in dataset:
                    paid_regd_no.append(row[1])
                rolls = MTRollLists_Staging.objects.filter(RegEventId_id=regeventid)
                unpaid_regd_no = rolls.exclude(student__RegNo__in=paid_regd_no)
                rolls = rolls.values_list('student__RegNo', flat=True)
                error_regd_no = set(paid_regd_no).difference(set(rolls))
                for regd_no in unpaid_regd_no:
                    not_registered = MTNotRegistered(Student=regd_no.student, RegEventId_id=regeventid, Registered=False)
                    not_registered.save()
                unpaid_regd_no = unpaid_regd_no.values_list('student__RegNo', flat=True) 
                MTStudentRegistrations_Staging.objects.filter(RegNo__in=unpaid_regd_no, RegEventId=regeventid).delete()
                MTRollLists_Staging.objects.filter(student__RegNo__in=unpaid_regd_no, RegEventId_id=regeventid).delete() 
                currentRegEvent = MTRegistrationStatus.objects.get(id=regeventid)
                currentRegEvent.RollListFeeStatus = 1
                currentRegEvent.save()
                return render(request, 'MTco_ordinator/RollListFeeUploadSuccess.html', {'errors':error_regd_no})      
    else:
        form = RollListFeeUploadForm(regIDs)
    return  render(request, 'MTco_ordinator/RollListFeeUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def rolllist_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs=None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear).exclude(RollListFeeStatus=0)
 
    if request.method == 'POST':
        form = RollListFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            regEvent = form.cleaned_data['regID']
            rolls = MTRollLists_Staging.objects.filter(RegEventId_id=regEvent)
            for roll in rolls:
                finalized_roll = MTRollLists(student=roll.student, RegEventId=roll.RegEventId)
                finalized_roll.save()
            reg_status_obj = MTRegistrationStatus.objects.get(id=regEvent)
            reg_status_obj.RollListStatus = 0
            reg_status_obj.save()
            return render(request, 'MTco_ordinator/RollListsFinalize.html', {'form':form, 'success':'Roll List has been successfully finalized.'})
    else:
        form = RollListFinalizeForm(regIDs)
    return render(request, 'MTco_ordinator/RollListsFinalize.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def RollList_Status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = MTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept)
    elif 'Co-ordinator' in groups:
        co_ordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, MYear=co_ordinator.MYear)
  
    if request.method == 'POST':
        form = RollListStatusForm(regIDs,request.POST)
        if(form.is_valid()):
            if request.POST['regID'] !='--Choose Event--':
                regEvent = form.cleaned_data['regID']
                strs = regEvent.split(':')
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
                years = {1:'I',2:'II'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2}
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
                rollListStatus=MTRollLists_Staging.objects.filter(RegEventId_id=currentRegEventId).order_by('student__RegNo')
                if request.POST.get('download'):
                    from MTco_ordinator.utils import RollListBookGenerator
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    response['Content-Disposition'] = 'attachment; filename=RollList({event}).xlsx'.format(event=regEvent)
                    BookGenerator = RollListBookGenerator(rollListStatus, regEvent)
                    workbook = BookGenerator.generate_workbook()
                    workbook.save(response)
                    return response
                return (render(request, 'MTco_ordinator/RollListStatus.html',{'form':form,'rolls': rollListStatus}))            
    form = RollListStatusForm(regIDs)
    return render(request, 'MTco_ordinator/RollListStatus.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def NotRegisteredStatus(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Mode='R')
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='R')
    elif 'Co-ordinator' in groups:
        co_ordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept, Mode='R')
   
    if request.method == 'POST':
        form = NotRegisteredStatusForm(regIDs,request.POST)
        if(form.is_valid):
            regEventId=request.POST.get('regID')
            not_regd_status=MTNotRegistered.objects.filter(RegEventId_id=regEventId).order_by('Student__RegNo')
            return (render(request, 'MTco_ordinator/NotRegisteredStatus.html',{'form': form, 'not_regd':not_regd_status}))            
    else:
        form = NotRegisteredStatusForm(regIDs)
    return render(request, 'MTco_ordinator/NotRegisteredStatus.html', {'form':form})
