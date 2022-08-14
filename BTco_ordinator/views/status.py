from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BThod.models import BTCoordinator
from BTsuperintendent.user_access_test import registration_status_access
from BTco_ordinator.forms import  RegularRegistrationsStatusForm, BacklogRegistrationSummaryForm, MakeupRegistrationSummaryForm
from BTco_ordinator.models import BTBacklogRegistrationSummary, BTRegularRegistrationSummary, BTMakeupRegistrationSummary
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTCycleCoordinator, BTProgrammeModel, BTHOD


# def is_Superintendent(user):
#     return user.groups.filter(name='Superintendent').exists()

# def logout_request(request):
#     logout(request)
#     return redirect("main:homepage")


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_makeup_registration_status(request,dept,year):
#     studentMakeupBacklogsVsRegistrations = BTStudentMakeupBacklogsVsRegistrations.objects.filter(BYear=year).filter(Dept=dept)
#     return render(request, 'SupExamDBRegistrations/DeptYearRegistrationStatus.html',
#                     { 'studentMakeupBacklogsVsRegistrations':studentMakeupBacklogsVsRegistrations }  )



@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def btech_regular_registration_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='R')
    elif 'Co-ordinator' in groups:
        cord = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cord.Dept, BYear=cord.BYear, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1, Mode='R')
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = RegularRegistrationsStatusForm(regIDs, request.POST)
        if(form.is_valid()):
            regId = form.cleaned_data['regId']
            if regId!='--Choose Event--':
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I', 2:'II', 3:'III', 4:'IV'}
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
                studymode = strs[6]
                deptObj = BTProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = BTRegularRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, BSem=bsem, Dept=dept).order_by('RegNo')
                
                if(byear>1):
                    studentRegistrations = studentRegistrations.order_by('RollNo')
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = RegularRegistrationsStatusForm(regIDs)
    return render(request, 'BTco_ordinator/BTRegularRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form}  )

@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def btech_backlog_registration_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='B')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='B')
    elif 'Co-ordinator' in groups:
        cord = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cord.Dept, BYear=cord.BYear, Mode='B')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1, Mode='B')
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = BacklogRegistrationSummaryForm(regIDs, request.POST)
        if(form.is_valid()):
            regId = form.cleaned_data['regId']
            if regId!='--Choose Event--':
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I', 2:'II', 3:'III', 4:'IV'}
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
                studymode = strs[6]
                deptObj = BTProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = BTBacklogRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, BSem=bsem, Dept=dept)
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = BacklogRegistrationSummaryForm(regIDs)
    return render(request, 'BTco_ordinator/BTBacklogRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )

@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def btech_makeup_registration_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='M')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='M')
    elif 'Co-ordinator' in groups:
        cord = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cord.Dept, BYear=cord.BYear, Mode='M')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1, Mode='M')
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = MakeupRegistrationSummaryForm(regIDs, request.POST)
        if(form.is_valid()):
            regId = form.cleaned_data['regId']
            if regId!='--Choose Event--':
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I', 2:'II', 3:'III', 4:'IV'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                strs = regId.split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[2])
                asem = int(strs[3])
                byear = rom2int[strs[1]]
                # bsem = rom2int[strs[2]]
                regulation = int(strs[4])
                mode = strs[5]
                deptObj = BTProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = BTMakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, Dept=dept)
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = MakeupRegistrationSummaryForm(regIDs)
    return render(request, 'BTco_ordinator/BTMakeupRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )


