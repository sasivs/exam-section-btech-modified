from django.contrib.auth.decorators import login_required, user_passes_test 
from ...SupExamDBRegistrations.views.home import is_Superintendent
from django.shortcuts import render, redirect
from django.http import HttpResponse
from co_ordinator.forms import NotPromotedListForm, NotPromotedUploadForm, NotPromotedUpdateForm, NotPromotedStatusForm
from co_ordinator.models import StudentGradePoints, NotPromoted, RollLists, StudentBacklogs, DroppedRegularCourses, \
    Subjects, StudentRegistrations
from superintendent.models import MandatoryCredits, RegistrationStatus
from co_ordinator.resources import NotPromotedResource
from django.db.models import Q
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from django.http.response import HttpResponse
# Import render module


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def not_promoted_list(request):
    if request.method == 'POST':
        form = NotPromotedListForm(request.POST)
        if form.is_valid():
            print("valid")
            event = form.cleaned_data['RegEvent']
            strs = event.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4} 
            dept = deptDict[strs[0]]
            ayear =int(strs[2])
            byear = rom2int[strs[1]]
            regulation = int(strs[3])
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,BYear=byear,Dept=dept,Regulation=regulation, Mode='R')
            rolls = RollLists.objects.filter(RegEventId__in=currentRegEventId)
            print(rolls)
            
            mandatory_credits = MandatoryCredits.objects.filter(Regulation=regulation, BYear=byear, Dept=dept)
            mandatory_credits = mandatory_credits[0].Credits
            np = []
            for roll in rolls:
                grades = StudentGradePoints.objects.filter(RegNo=roll.student.RegNo, AYear=ayear, BYear=byear).filter(~Q(Grade='F')).\
                    filter(~Q(Grade='I')).filter(~Q(Grade='X')).filter(~Q(Grade='R'))
                credits=0
                for g in grades:
                    credits += g.Credits
                if credits < mandatory_credits:
                    d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'R'}
                    np.append(d)
                else:
                    if byear == 2 or byear == 3:
                        backlogs = StudentBacklogs.objects.filter(RegNo=roll.student.RegNo, BYear=byear-1)
                        if len(backlogs) != 0:
                            d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'B'}
                            np.append(d)
                        else:
                            dropped_courses = DroppedRegularCourses.objects.filter(RegNo=roll.student.RegNo)
                            for course in dropped_courses:
                                sub = Subjects.objects.get(id=course.sub_id)
                                offeredEvent = RegistrationStatus.objects.get(id=sub.RegEventId)
                                if offeredEvent.BYear == byear-1:
                                    check_registration = StudentRegistrations.objects.filter(RegNo=roll.student.RegNo, sub_id=course.sub_id)
                                    if len(check_registration) == 0:
                                        d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'B'}
                                        np.append(d)
                    elif byear == 4:
                        backlogs = StudentBacklogs.objects.filter(RegNo=roll.student.RegNo)
                        if len(backlogs) != 0:
                            d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'B'}
                            np.append(d)
                        else:
                            dropped_courses = DroppedRegularCourses.objects.filter(RegNo=roll.student.RegNo)
                            for course in dropped_courses:
                                sub = Subjects.objects.get(id=course.sub_id)
                                check_registration = StudentRegistrations.objects.filter(RegNo=roll.student.RegNo, sub_id=course.sub_id)
                                if len(check_registration) == 0:
                                    d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'B'}
                                    np.append(d)
            if request.POST.get('download'):
                    from SupExamDBRegistrations.utils import NotPromotedBookGenerator
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    response['Content-Disposition'] = 'attachment; filename=NotPromoted({regevent}).xlsx'.format(regevent=event)
                    BookGenerator = NotPromotedBookGenerator(np, regulation, event)
                    workbook = BookGenerator.generate_workbook()
                    workbook.save(response)
                    return response
            return render(request, 'co_ordinator/NotPromotedList.html', {'form':form, 'notPromoted':np})
    else:
        form = NotPromotedListForm()
    return render(request, 'co_ordinator/NotPromotedList.html', {'form':form})



def not_promoted_upload(request):
    if request.method == 'POST':
        form = NotPromotedUploadForm(request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['RegEvent']!='-- Select Registration Event --':
            regEvent = form.cleaned_data['RegEvent']
            strs = regEvent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4} 
            dept = deptDict[strs[0]]
            ayear =int(strs[2])
            byear = rom2int[strs[1]]
            regulation = int(strs[3])
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            newDataset= Dataset()
            newDataset.headers =['student', 'AYear', 'BYear', 'Regulation','PoA']
            errorDataset = Dataset()
            errorDataset.headers=['student_id', 'RegNo', 'AYear', 'BYear', 'Regulation', 'PoA']
            for i in range(len(dataset)):
                row = dataset[i]
                print(row)
                if row[2] == ayear and row[3] == byear and row[4] == regulation:
                    newRow = (row[0],row[2],row[3], row[4], row[5])
                    newDataset.append(newRow)
                else:
                    newRow = (row[0],row[1],row[2],row[3],row[4],row[5])
                    errorDataset.append(newRow)
            not_promoted_resource = NotPromotedResource()
            result = not_promoted_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                not_promoted_resource.import_data(newDataset, dry_run=False)
                if (len(errorDataset)!=0):
                    print("here")
                    npErrRows = [(errorDataset[i][0],errorDataset[i][1],errorDataset[i][2],errorDataset[i][3], errorDataset[i][4], errorDataset[i][5]) for i in range(len(errorDataset))]
                    request.session['npErrRows'] = npErrRows
                    request.session['RegEvent'] = regEvent
                    return redirect('NotPromotedUploadErrorHandler' )
                return(render(request,'co_ordinator/NotPromotedUploadSuccess.html'))
            else:
                print("here1")

                errors = result.row_errors()
                print(errors[0][1][0].error)
                indices = set([i for i in range(len(newDataset))])    
                errorIndices = set([i[0]-1 for i in errors])
                print(errors[0][0])
                cleanIndices = indices.difference(errorIndices)
                cleanDataset = Dataset()
                for i in list(cleanIndices):
                    cleanDataset.append(newDataset[i])
                cleanDataset.headers = newDataset.headers
                
                result1 = not_promoted_resource.import_data(cleanDataset, dry_run=True)
                if not result1.has_errors():
                    not_promoted_resource.import_data(cleanDataset, dry_run=False)
                else:
                        print('Something went wrong in plain import')
                errorData = Dataset()
                for i in list(errorIndices):
                    newRow = (newDataset[i][0],dataset[i][1],newDataset[i][1],newDataset[i][2],newDataset[i][3], newDataset[i][4])
                    errorData.append(newRow)
                for i in errorDataset:
                    errorData.append(i)
                npErrRows = [(errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3], errorData[i][4], errorData[i][5]) for i in range(len(errorData))]
                request.session['npErrRows'] = npErrRows
                request.session['RegEvent'] = regEvent
                return redirect('NotPromotedUploadErrorHandler')
    else:
        form = NotPromotedUploadForm()
    return render(request, 'co_ordinator/NotPromotedUpload.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def not_promoted_upload_error_handler(request):
    npErrRows = request.session.get('npErrRows')
    regEvent = request.session.get('RegEvent')
    if(request.method=='POST'):
        form = NotPromotedUpdateForm(npErrRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(npErrRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    NotPromoted.objects.filter(student_id=fRow[0],AYear=fRow[2], BYear=fRow[3], Regulation=fRow[4]).update(PoA=fRow[5])
            return render(request, 'co_ordinator/NotPromotedUploadSuccess.html')
    else:
        form = NotPromotedUpdateForm(Options=npErrRows)
    return(render(request, 'co_ordinator/NotPromotedUploadErrorHandler.html',{'form':form}))

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def not_promoted_status(request):
    if(request.method=='POST'):
        form = NotPromotedStatusForm(request.POST)
        # if(form.is_valid()):
        if(request.POST['RegEvent']!='-- Select Registration Event --'):
            regEvent = request.POST['RegEvent']
            strs = regEvent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4} 
            dept = deptDict[strs[0]]
            ayear =int(strs[2])
            byear = rom2int[strs[1]]
            regulation = int(strs[3])
            notPromoted = NotPromoted.objects.filter(AYear=ayear, BYear=byear, Regulation=regulation)
            return render(request, 'co_ordinator/NotPromotedStatus.html', {'notPromoted':notPromoted, 'form':form})
    else:
        form = NotPromotedStatusForm()
    return render(request, 'co_ordinator/NotPromotedStatus.html', {'form':form})


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def not_promoted_backlog_mode_regs(request):
#     studentInfo = []
#     if(request.method == 'POST'):
#         regId = request.POST['RegEvent']
#         strs = regId.split(':')
#         depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
#         years = {1:'I',2:'II',3:'III',4:'IV'}
#         deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
#         rom2int = {'I':1,'II':2,'III':3,'IV':4}
#         strs = regId.split(':')
#         dept = deptDict[strs[0]]
#         ayear = int(strs[3])
#         asem = int(strs[4])
#         byear = rom2int[strs[1]]
#         bsem = rom2int[strs[2]]
#         regulation = int(strs[5])
#         mode = strs[6]
#         currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
#                     Dept=dept,Mode=mode,Regulation=regulation)
#         currentRegEventId = currentRegEventId[0].id
#         con = {} 
#         if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
#             con['RegEvent']=request.POST['RegEvent']
#             if 'RegNo' in request.POST.keys():
#                 con['RegNo']=request.POST['RegNo']
#             form = NotPromotedBacklogRegistrationForm(con)
#         elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
#             form = NotPromotedBacklogRegistrationForm(request.POST)
#         if not 'RegNo' in request.POST.keys():
#             pass 
#         elif not 'Submit' in request.POST.keys():
#             regNo = request.POST['RegNo']
#             event = (request.POST['RegEvent'])
#             print(regNo, event)
#             studentInfo = StudentInfo.objects.filter(RegNo=regNo)
#         elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
#             regNo = request.POST['RegNo']
#             event = (request.POST['RegEvent'])
#             studentInfo = StudentInfo.objects.filter(RegNo=regNo) 
#             studyModeCredits = 0
#             examModeCredits = 0
#             for sub in form.myFields:
#                 if(form.cleaned_data['Check'+str(sub[9])]):
#                     if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
#                         if(form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
#                             studyModeCredits += sub[2]
#                         else:
#                             examModeCredits += sub[2]
#                     else:
#                         form = NotPromotedBacklogRegistrationForm(request.POST)
#                         context = {'form':form, 'msg': 2}  
#                         if(len(studentInfo)!=0):
#                             context['RollNo'] = studentInfo[0].RollNo
#                             context['Name'] = studentInfo[0].Name  
#                         return render(request, 'co_ordinator/BTBacklogRegistration.html',context)
#             if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
#                 for sub in form.myFields:
#                     if sub[6] == 'D':
#                         if form.cleaned_data['Check'+str(sub[9])] == False:
#                             StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], \
#                                 id=sub[10]).delete()
#                     else:   #Handling Backlog Subjects
#                         if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
#                             #update operation mode could be study mode or exam mode
#                             StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], \
#                                 sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+str(sub[9])])
#                         elif(sub[5]):
#                             #delete record from registration table
#                             StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], \
#                                 sub_id = sub[9], id=sub[10]).delete()
#                         elif(form.cleaned_data['Check'+str(sub[9])]):
#                             #insert backlog registration
#                             if sub[10]=='':
#                                 newRegistration = StudentRegistrations_Staging(RegNo = request.POST['RegNo'],RegEventId=currentRegEventId,\
#                                 Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
#                                 newRegistration.save()                   
#                 return(render(request,'co_ordinator/BTBacklogRegistrationSuccess.html'))
#             else:
#                 form = NotPromotedBacklogRegistrationForm(request.POST)
#                 context = {'form':form, 'msg':1}
#                 context['study']=studyModeCredits
#                 context['exam']=examModeCredits
#                 if(len(studentInfo)!=0):
#                     context['RollNo'] = studentInfo[0].RollNo
#                     context['Name'] = studentInfo[0].Name  
#                 return render(request, 'co_ordinator/BTBacklogRegistration.html',context)
#         else:
#             print("form validation failed")   
#             print(form.errors.as_data())          
#     else:
#         form = NotPromotedBacklogRegistrationForm()
#     context = {'form':form, 'msg':0}
#     if(len(studentInfo)!=0):
#         context['RollNo'] = studentInfo[0].RollNo
#         context['Name'] = studentInfo[0].Name  
#     return render(request, 'co_ordinator/BTBacklogRegistration.html',context)