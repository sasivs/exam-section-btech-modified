from typing import Set
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse

import SupExamDBRegistrations
from ..forms import BacklogRegistrationForm, DBYBSAYASSelectionForm, DeptElectiveRegsForm, FirstYearBacklogRegistrationForm,\
     RegistrationForm1, StudentCancellationForm, StudentRegistrationUpdateForm,RegistrationsUploadForm, TestForm,\
          RegistrationsFinalizeEventForm, OpenElectiveRegistrationsForm
from ..models import CurrentAcademicYear, RegistrationStatus, RollLists_Staging, StudentBacklogs, StudentCancellation, \
    StudentGrades, StudentInfo, StudentMakeupBacklogsVsRegistrations,\
     StudentRegistrations,  ProgrammeModel, Subjects_Staging, \
         RollLists, Subjects, StudentRegistrations_Staging
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from SupExamDB.forms import DeptYearSelectionForm
from django.db.models import F, Q
from .home import is_Superintendent

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def dept_elective_regs_all(request):
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
        form = DeptElectiveRegsForm(subjects,data)
        if regId != '--Choose Event--' and subId != '--Select Subject--':
            print(subId)
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

            rolls = RollLists_Staging.objects.filter(RegEventId_id=currentRegEventId)
            for i in rolls:
                reg = StudentRegistrations_Staging(RegNo=i.student.RegNo, RegEventId=currentRegEventId, Mode=1,sub_id=subId)
                reg.save()
            rolls = rolls.values_list('student__RegNo', flat=True)
            StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId).exclude(RegNo__in=rolls).delete()
            return render(request, 'SupExamDBRegistrations/Dec_Regs_success.html')
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
            subjects = Subjects.objects.filter(RegEventId=currentRegEventId, Category='DEC')
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            form = DeptElectiveRegsForm(subjects,data)
    else:
        form = DeptElectiveRegsForm()
    return render(request, 'SupExamDBRegistrations/Dec_register_all.html',{'form':form})