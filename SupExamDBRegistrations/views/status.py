from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse

import SupExamDBRegistrations
from ..forms import  BRegistrationsEventForm, RegistrationsEventForm
from ..models import BacklogRegistrationSummary, ProgrammeModel, StudentMakeupBacklogsVsRegistrations, RegularRegistrationSummary
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from SupExamDB.forms import DeptYearSelectionForm
from django.db.models import F



def is_Superintendent(user):
    return user.groups.filter(name='Superintendent').exists()

def logout_request(request):
    logout(request)
    return redirect("main:homepage")


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_makeup_registration_status(request,dept,year):
    studentMakeupBacklogsVsRegistrations = StudentMakeupBacklogsVsRegistrations.objects.filter(BYear=year).filter(Dept=dept)
    return render(request, 'SupExamDBRegistrations/DeptYearRegistrationStatus.html',
                    { 'studentMakeupBacklogsVsRegistrations':studentMakeupBacklogsVsRegistrations }  )

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_regular_registration_status(request):
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = RegistrationsEventForm(request.POST)
        if(form.is_valid()):
            print('Valid')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = form.cleaned_data['regID'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            mode = strs[5]
            if(mode=='R'):
                deptObj = ProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                #print(deptObj)
                heading = 'Regular Registrations for ' + deptObj[0]['Specialization'] + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = RegularRegistrationSummary.objects.filter(AYear=ayear, ASem = asem, BYear=byear, BSem = bsem, Dept = dept).values()

    else:
        form = RegistrationsEventForm()
    return render(request, 'SupExamDBRegistrations/Status/BTRegularRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_registration_status_home(request):
    return render(request, 'SupExamDBRegistrations/Status/registrationstatus.html')
@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_backlog_registration_status(request):
    heading = ''
    studentRegistrations = []
    if(request.method=='POST'):
        form = BRegistrationsEventForm(request.POST)
        if(form.is_valid()):
            print('Valid')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I', 2:'II', 3:'III', 4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            strs = form.cleaned_data['regID'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            mode = strs[5]
            studymode = strs[6]
            if(mode=='R'):
                deptObj = ProgrammeModel.objects.filter(Dept=dept,ProgrammeType='UG').values()
                #print(deptObj)
                heading = ' Registrations for ' + deptObj[0]['Specialization'] + str(ayear) + '-'+str(ayear+1) + ' ' + strs[4] + ' Semester'
                studentRegistrations = BacklogRegistrationSummary.objects.filter(AYear=ayear, ASem = asem).values()

    else:
        form = RegistrationsEventForm()
    return render(request, 'SupExamDBRegistrations/Status/BTRegularRegistrationStatus.html',
                    { 'studentRegistrations':studentRegistrations ,'form':form, 'heading' :heading }  )


