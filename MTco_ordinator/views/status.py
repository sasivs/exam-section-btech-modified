from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MThod.models import MTCoordinator
from MTsuperintendent.user_access_test import is_Superintendent, registration_status_access
from MTco_ordinator.forms import  RegularRegistrationsStatusForm, BacklogRegistrationSummaryForm, MakeupRegistrationSummaryForm
from MTco_ordinator.models import MTBacklogRegistrationSummary, MTRegularRegistrationSummary, MTMakeupRegistrationSummary
from MTsuperintendent.models import  MTProgrammeModel, MTRegistrationStatus, MTHOD




@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def mtech_regular_registration_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups:
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Mode='R')
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='R')
    elif 'Co-ordinator' in groups:
        cord = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=cord.Dept, MYear=cord.MYear, Mode='R')
   
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = RegularRegistrationsStatusForm(regIDs, request.POST)
        if(form.is_valid()):
            regId = form.cleaned_data['regId']
            if regId!='--Choose Event--':
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME']
                years = {1:'I', 2:'II'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2}
                strs = regId.split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                myear = rom2int[strs[1]]
                msem = rom2int[strs[2]]
                regulation = int(strs[5])
                mode = strs[6]
                studymode = strs[6]
                deptObj = MTProgrammeModel.objects.filter(Dept=dept,ProgrammeType='PG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = MTRegularRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, MYear=myear, MSem=msem, Dept=dept).order_by('RegNo')
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = RegularRegistrationsStatusForm(regIDs)
    return render(request, 'MTco_ordinator/BTRegularRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form}  )

@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def mtech_backlog_registration_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups:
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Mode='B')
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='B')
    elif 'Co-ordinator' in groups:
        cord = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=cord.Dept, MYear=cord.MYear, Mode='B')
   
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = BacklogRegistrationSummaryForm(regIDs, request.POST)
        if(form.is_valid()):
            regId = form.cleaned_data['regId']
            if regId!='--Choose Event--':
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
                years = {1:'I', 2:'II'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2}
                strs = regId.split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                myear = rom2int[strs[1]]
                msem = rom2int[strs[2]]
                regulation = int(strs[5])
                mode = strs[6]
                studymode = strs[6]
                deptObj = MTProgrammeModel.objects.filter(Dept=dept,ProgrammeType='PG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = MTBacklogRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, MYear=myear, MSem=msem, Dept=dept)
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = BacklogRegistrationSummaryForm(regIDs)
    return render(request, 'MTco_ordinator/BTBacklogRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )

@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def mtech_makeup_registration_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups:
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Mode='M')
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='M')
    elif 'Co-ordinator' in groups:
        cord = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=cord.Dept, MYear=cord.MYear, Mode='M')
   
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = MakeupRegistrationSummaryForm(regIDs, request.POST)
        if(form.is_valid()):
            regId = form.cleaned_data['regId']
            if regId!='--Choose Event--':
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
                years = {1:'I', 2:'II'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2}
                strs = regId.split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[2])
                asem = int(strs[3])
                myear = rom2int[strs[1]]
                # msem = rom2int[strs[2]]
                regulation = int(strs[4])
                mode = strs[5]
                deptObj = MTProgrammeModel.objects.filter(Dept=dept,ProgrammeType='PG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = MTMakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, MYear=myear, Dept=dept)
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = MakeupRegistrationSummaryForm(regIDs)
    return render(request, 'MTco_ordinator/BTMakeupRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )


