from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from SupExamDBRegistrations.forms import BacklogRegistrationForm, RegistrationsEventForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, DroppedRegularRegistrationsForm,\
        MakeupRegistrationsForm
from SupExamDBRegistrations.models import RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, \
    SubjectStagingResource, Subjects, Subjects_Staging, DroppedRegularCourses, StudentRegistrations_Staging
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def makeup_registrations(request):
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
        currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
        currentRegEventId = currentRegEventId[0].id
        con = {} 
        if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
            con['RegEvent']=request.POST['RegEvent']
            if 'RegNo' in request.POST.keys():
                con['RegNo']=request.POST['RegNo']
            form = MakeupRegistrationsForm(con)
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
            form = MakeupRegistrationsForm(request.POST)
        if 'RegNo' not in request.POST.keys() :
            pass
        elif request.POST['RegNo'] != '--Select Reg Number--' and 'Submit' not in request.POST.keys():
            pass
        elif request.POST['RegNo'] != '--Select Reg Number--' and 'Submit' in request.POST.keys() and form.is_valid():
            for sub in form.myFields:
                already_registered = StudentRegistrations_Staging.objects.filter(RegNo=request.POST['RegNo'], \
                        sub_id=sub[8], RegEventId=currentRegEventId)
                if form.cleaned_data['Check'+str(sub[8])]:
                    if len(already_registered) == 0:
                        newReg = StudentRegistrations_Staging(RegNo=request.POST['RegNo'], sub_id=sub[8],\
                            Mode=form.cleaned_data['RadioMode'+str(sub[8])], RegEventId=currentRegEventId)
                        newReg.save()
                else:
                    if len(already_registered) != 0:
                        StudentRegistrations_Staging.objects.get(id=already_registered[0].id).delete()
            return render(request, 'SupExamDBRegistrations/MakeupRegistrationsSuccess.html')
    elif request.method == 'POST':
        form = MakeupRegistrationsForm(request.POST)
    else:
        form = MakeupRegistrationsForm()
    return render(request, 'SupExamDBRegistrations/MakeupRegistrations.html', {'form':form})