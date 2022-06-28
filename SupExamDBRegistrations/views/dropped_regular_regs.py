from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from SupExamDBRegistrations.forms import BacklogRegistrationForm, RegistrationsEventForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, DroppedRegularRegistrationsForm
from SupExamDBRegistrations.models import RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, \
     Subjects, Subjects_Staging, DroppedRegularCourses, StudentRegistrations_Staging
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def dropped_regular_registrations(request):
    studentInfo = []
    if(request.method == 'POST'):
        print(request.POST)
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
        con = {key:request.POST[key] for key in request.POST.keys()} 
        if('RegNo' in request.POST.keys()):
            droppedCourses = DroppedRegularCourses.objects.filter(RegNo=request.POST['RegNo'])
            reg_status = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
            studentRegistrations=[]
            for regevent in reg_status:
                studentRegistrations += list(StudentRegistrations_Staging.objects.filter(RegNo=request.POST['RegNo'],RegEventId=regevent.id))
            studentRegularRegistrations = []
            for regn in studentRegistrations:
                regEvent = RegistrationStatus.objects.get(id=regn.RegEventId)
                if (regEvent.Mode == 'R' or regEvent.Mode == 'D'):
                    studentRegularRegistrations.append(regn)
            for row in droppedCourses:
                for entry in studentRegistrations:
                    if row.sub_id == entry. sub_id:
                        con[str('RadioMode'+row.sub_id)] = list(str(entry.Mode))

        form = DroppedRegularRegistrationsForm(con)
        if not 'RegNo' in request.POST.keys():
            pass 
        elif not 'Submit' in request.POST.keys():
            regNo = request.POST['RegNo']
            event = (request.POST['RegEvent'])
            studentInfo = StudentInfo.objects.filter(RegNo=regNo)
        elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
            regNo = request.POST['RegNo']
            event = (request.POST['RegEvent'])
            studentInfo = StudentInfo.objects.filter(RegNo=regNo) 
            studyModeCredits = 0
            examModeCredits = 0
            for sub in form.myFields:
                if(form.cleaned_data['Check'+str(sub[9])]):
                    if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
                        if (form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
                            studyModeCredits += sub[2]
                        else:
                            examModeCredits += sub[2]
                    else:
                        form = DroppedRegularRegistrationsForm(request.POST)
                        context = {'form':form, 'msg': 2}  
                        if(len(studentInfo)!=0):
                            context['RollNo'] = studentInfo[0].RollNo
                            context['Name'] = studentInfo[0].Name  
                        return render(request, 'SupExamDBRegistrations/DroppedRegularReg.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        regular_sub = Subjects.objects.get(id=sub[9])
                        if(form.cleaned_data['Check'+str(sub[9])] == False):
                            #delete regular_record from the registration table
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=regular_sub.RegEventId,\
                                 sub_id = sub[9], id=sub[10])
                            if len(reg) != 0:
                                StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=regular_sub.RegEventId,\
                                     sub_id = sub[9], id=sub[10]).delete()
                                new_dropped_course = DroppedRegularCourses(RegNo=request.POST['RegNo'], sub_id=sub[9])
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if(len(reg) == 0):
                                newRegistration = StudentRegistrations_Staging(RegNo = request.POST['RegNo'], RegEventId = currentRegEventId,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                                newRegistration.save()
                        else:
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if len(reg) != 0:
                                StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                     sub_id = sub[9]).delete()
                    else:   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+sub[0]])
                        elif(sub[5]):
                            #delete record from registration table
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], id=sub[10]).delete()  
                return(render(request,'SupExamDBRegistrations/DroppedRegularRegSuccess.html'))
            else:
                form = DroppedRegularRegistrationsForm(request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(len(studentInfo)!=0):
                    context['RollNo'] = studentInfo[0].RollNo
                    context['Name'] = studentInfo[0].Name  
                return render(request, 'SupExamDBRegistrations/DroppedRegularReg.html',context)
        else:
            print("form validation failed")             
    else:
        form = DroppedRegularRegistrationsForm()
    context = {'form':form}
    if(len(studentInfo)!=0):
        context['RollNo'] = studentInfo[0].RollNo
        context['Name'] = studentInfo[0].Name  
    return render(request, 'SupExamDBRegistrations/DroppedRegularReg.html',context)