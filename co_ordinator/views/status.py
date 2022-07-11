from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from superintendent.user_access_test import is_Superintendent
from co_ordinator.forms import RegularRegistrationsStatusForm, BacklogRegistrationSummaryForm, MakeupRegistrationSummaryForm
from co_ordinator.models import BacklogRegistrationSummary, RegularRegistrationSummary, MakeupRegistrationSummary
from superintendent.models import ProgrammeModel


# def is_Superintendent(user):
#     return user.groups.filter(name='Superintendent').exists()

# def logout_request(request):
#     logout(request)
#     return redirect("main:homepage")


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_makeup_registration_status(request,dept,year):
#     studentMakeupBacklogsVsRegistrations = StudentMakeupBacklogsVsRegistrations.objects.filter(BYear=year).filter(Dept=dept)
#     return render(request, 'SupExamDBRegistrations/DeptYearRegistrationStatus.html',
#                     { 'studentMakeupBacklogsVsRegistrations':studentMakeupBacklogsVsRegistrations }  )

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_registration_status_home(request):
    return render(request, 'SupExamDBRegistrations/Status/registrationstatus.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_regular_registration_status(request):
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = RegularRegistrationsStatusForm(request.POST)
        if(form.is_valid()):
            studentRegistrations = []
            ayear = form.cleaned_data['aYear'] 
            if ayear!=0:
                studentRegistrations = RegularRegistrationSummary.objects.filter(AYear=ayear)
                asem = form.cleaned_data['aSem']
                if asem!=0:
                    studentRegistrations = studentRegistrations.filter(ASem=int(asem))
                dept = form.cleaned_data['dept']
                if dept!=0:
                    studentRegistrations = studentRegistrations.filter(Dept=int(dept))
                regNo = form.cleaned_data['regNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=int(regNo))
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = RegularRegistrationsStatusForm()
    return render(request, 'co_ordinator/BTRegularRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form}  )

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_backlog_registration_status(request):
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = BacklogRegistrationSummaryForm(request.POST)
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
                deptObj = ProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = BacklogRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, BSem=bsem, Dept=dept)
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = BacklogRegistrationSummaryForm()
    return render(request, 'co_ordinator/BTBacklogRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_makeup_registration_status(request):
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = MakeupRegistrationSummaryForm(request.POST)
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
                deptObj = ProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + ': ' + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = MakeupRegistrationSummary.objects.filter(Regulation=regulation,AYear=ayear, \
                    ASem = asem, BYear=byear, Dept=dept)
                regNo = form.cleaned_data['RegNo']
                if regNo != 0:
                    studentRegistrations = studentRegistrations.filter(RegNo=regNo)
                studentRegistrations = list(studentRegistrations.values())
    else:
        form = MakeupRegistrationSummaryForm()
    return render(request, 'co_ordinator/BTMakeupRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )


