from typing import Set
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse

import SupExamDBRegistrations
from ..forms import BacklogRegistrationForm, DBYBSAYASSelectionForm, FirstYearBacklogRegistrationForm,\
     RegistrationForm1, StudentCancellationForm, StudentRegistrationUpdateForm,RegistrationsUploadForm, TestForm,\
          RegistrationsFinalizeEventForm, OpenElectiveRegistrationsForm
from ..models import CurrentAcademicYear, RegistrationStatus, StudentBacklogs, StudentCancellation, \
    StudentGrades, StudentInfo, StudentMakeupBacklogsVsRegistrations,\
     StudentRegistrations, StudentRegistrationsResource, ProgrammeModel, SubjectStagingResource, Subjects_Staging, \
         RollLists, Subjects, StudentRegistrations_Staging
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from SupExamDB.forms import DeptYearSelectionForm
from django.db.models import F, Q
from .home import is_Superintendent

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def open_elective_regs(request):
    necessary_field_msg = False
    subjects=[]
    if(request.method == "POST"):
        print(request.POST)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2,'III':3,'IV':4}
        regId = request.POST['regID']
        subId = request.POST['subId']
        print(subId)
        data = {'regID':regId, 'subId':subId}
        form = OpenElectiveRegistrationsForm(subjects,data)
        if 'file' not in request.POST.keys():
            file = request.FILES['file']   
            print(file)
        else:
            file = request.POST['file']
        if regId != '--Choose Event--' and subId != '--Select Subject--' and file != '':
            print(subId)
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            for i in range(len(dataset)):
                regNo = int(dataset[i][0])
                reg = StudentRegistrations_Staging(RegNo=regNo, RegEventId=currentRegEventId, Mode=1,sub_id=subId)
                reg.save()
            return render(request, 'SupExamDBRegistrations/OecRegistrationsSuccess.html')
        elif regId != '--Choose Event--':
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
            subjects = Subjects.objects.filter(RegEventId=currentRegEventId, Category='OEC')
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            print(subjects)
            form = OpenElectiveRegistrationsForm(subjects,data)
    else:
        form = OpenElectiveRegistrationsForm()
    return render(request, 'SupExamDBRegistrations/OpenElectiveRegistrations.html',{'form':form,'msg':necessary_field_msg})

# def open_elective_regs_finalize(request):
#     subId = request.session.get('sub_id')
#     ayasbym = request.session.get('ayasbym')
#     ayear = ayasbym[0]
#     asem = ayasbym[1]
#     byear = ayasbym[2]
#     mode = ayasbym[3]
#     if request.method == 'POST':
#         return
#     else:
#         regs = StudentRegistrations_Staging.objects.filter(AYear=ayear,ASem=asem,BYear=byear,Mode=mode,sub_id=subId).values()
#         form = OpenElectiveRegsFinalizeForm(regs)
#     return render(request, 'SupExamDBRegistrations/OecFinalize.html',{'form':form})