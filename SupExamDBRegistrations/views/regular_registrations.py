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
          RegistrationsFinalizeEventForm
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
def btech_regular_registration(request):
    if(request.method=='POST'):
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        form = RegistrationsUploadForm(regIDs, request.POST)
        if(form.is_valid()):
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,byear,bsem,dept,mode, regulation) = regIDs[int(form.cleaned_data['regID'])]
                print(regIDs[int(form.cleaned_data['regID'])])
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                mode = 1
                if(byear==1):
                    rolls = RollLists.objects.filter(AYear=ayear,BYear=byear,Cycle=dept,Regulation=regulation)
                    subs = Subjects.objects.filter(~Q(Category='OEC'),RegEventId=currentRegEventId).filter(~Q(Category='DEC'))
                    print(subs[0].id)
                    for roll in rolls:
                        for sub in subs:
                            regRow = StudentRegistrations_Staging(RegNo=roll.RegNo, Mode=mode, RegEventId=currentRegEventId, sub_id=sub.id)
                            regRow.save()
                    return render(request, 'SupExamDBRegistrations/BTRegistrationUploadSuccess.html')
                else:
                    rolls = RollLists.objects.filter(AYear=ayear,BYear=byear,Dept=dept, Regulation=regulation)
                    subs = Subjects.objects.filter(~Q(Category='OEC'),RegEventId=currentRegEventId).filter(~Q(Category='DEC'))
                    print(subs[0].id)
                    for roll in rolls:
                        for sub in subs:
                            regRow = StudentRegistrations_Staging(RegNo=roll.RegNo, Mode=mode, RegEventId=currentRegEventId, sub_id=sub.id)
                            regRow.save()
                    return render(request, 'SupExamDBRegistrations/BTRegistrationUploadSuccess.html')
    else:
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        form = RegistrationsUploadForm(Options=regIDs)
    return(render(request, 'SupExamDBRegistrations/BTRegularRegistrationUpload.html',{'form':form }))


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def registrations_finalize(request):
    if(request.method=='POST'):
        form = RegistrationsFinalizeEventForm(request.POST)
        if(form.is_valid()):
            print('valid form')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            if(form.cleaned_data['regID']!='--Choose Event--'):
                strs = form.cleaned_data['regID'].split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                regulation=int(strs[5])
                mode = strs[6]
                regs = []
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                regs = StudentRegistrations_Staging.objects.filter(RegEventId=currentRegEventId)

                for reg in regs:
                    s=StudentRegistrations(RegNo=reg.RegNo, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                    s.save() 
                return render(request, 'SupExamDBRegistrations/BTRegistrationsFinalizeSuccess.html')
        else:
            print('Invalid')
    else:
        form = RegistrationsFinalizeEventForm()
    return render(request, 'SupExamDBRegistrations/BTRegistrationsFinalize.html',{'form':form})
    
    


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def makeup_registrations(request):
    return HttpResponse('<b> Simple Response </b>')




@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def get_btbacklog_regnos(request,dept,byear):
    studentBacklogs = StudentBacklogs.objects.filter(BYear=byear,Dept=dept).values('RegNo','RollNo').distinct()
    studentBacklogs = list(studentBacklogs)
    print(studentBacklogs)
    return JsonResponse({'data':studentBacklogs}, safe=False)

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def get_btregistered_subjects(request, regNo):
    backlogSubjects = StudentBacklogs.objects.filter(RegNo=regNo).values()
    backlogSubjects = list(backlogSubjects)
    regularSubjects = list(StudentRegistrations.objects.filter(RegNo=regNo).values())
    totalSubjects = regularSubjects+backlogSubjects
    return JsonResponse({'data':backlogSubjects}, safe=False)

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def test_page(request):
    if(request.method=='POST'):
        print(request.POST)
        form = TestForm(request.POST)
        if(form.is_valid()):
            print(form.cleaned_data['YrSelect'])
            print(form.cleaned_data['MonthSelect'])
        else:
            print("form validation failed")
    else:
        form = TestForm()
    return render(request, 'SupExamDBRegistrations/BTTest.html', {'form': form})

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_backlog_registration_page(request, regNo):
#     #regNo = 952406
#     print(request.user.username)
#     #coordinatorDetails = CoordinatorInfo.objects.filter(UserId=request.user.username)[0]
#     if(request.method=='POST'):
#         studentBacklogs = StudentBacklogs.objects.filter(RegNo=regNo).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
#         choices = [(studentBacklogs[i].SubCode, studentBacklogs[i].SubName, studentBacklogs[i].Credits,
#                         studentBacklogs[i].Grade ) for i in range(len(studentBacklogs))]
        
#         form = RegistrationForm1(regNo,choices,{}, request.POST)
        
#         if(form.is_valid()):
#             AYear=CurrentAcademicYear.objects.all()
#             #print(form.cleaned_data['Choices'])
#             StudentRegistrations.objects.filter(RegNo=regNo).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year).delete()
#             StudentMakeupMarks.objects.filter(RegNo=regNo).filter(Dept=coordinatorDetails.Dept).filter(BYear=coordinatorDetails.Year).delete()
#             for cIndex, choice in enumerate(choices):
#                 print(form.cleaned_data.get('RadioMode'+choice[0]))
#                 if(form.cleaned_data.get('Check'+choice[0])):
#                     print(form.cleaned_data.get('Check'+choice[0]))
#                     print(form.cleaned_data.get('RadioMode'+choice[0]))
                  
#                     subjectTobeInserted = studentBacklogs.filter(SubCode=choice[0])
#                     newRegistration = StudentRegistrations(RegNo=subjectTobeInserted[0].RegNo,
#                                 SubCode=subjectTobeInserted[0].SubCode,
#                                 AYear=2021,
#                                 ASem=1,
#                                 OfferedYear=subjectTobeInserted[0].OfferedYear,
#                                 Dept=subjectTobeInserted[0].Dept,
#                                 BYear=subjectTobeInserted[0].BYear,
#                                 Regulation=subjectTobeInserted[0].Regulation,
#                                 BSem = subjectTobeInserted[0].BSem,
#                                 Mode = form.cleaned_data.get('RadioMode'+choice[0]))
#                     newRegistration.save()          
#             return render(request, 'Registrations/success_page.html')    
#         else:
#             print('Form not valid in POST')
#     else:
#         AYear=CurrentAcademicYear.objects.all()
#         studentInfo = StudentInfo.objects.filter(RegNo=regNo)
#         studentBacklogs = StudentBacklogs.objects.filter(RegNo=regNo).filter(BYear = coordinatorDetails.Year).filter(Dept=coordinatorDetails.Dept)
#         studentRegistrations = StudentRegistrations.objects.filter(RegNo=regNo,AYear=2021,ASem=1)
#         choices = [(studentBacklogs[i].SubCode,studentBacklogs[i].Grade ) for i in range(len(studentBacklogs))]

#         subDetails = [ (studentBacklogs[i].SubCode,
#                         studentBacklogs[i].SubName, str(studentBacklogs[i].Credits), studentBacklogs[i].Grade) for i in range(len(studentBacklogs))]
     
#         selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
       
#         form = RegistrationForm1(RegNo=studentInfo[0].RegNo, Options = subDetails, Selection=selection )
#         #print(form)

#     return render(request, 'Registrations/test.html', {'form': form, 'subjectList':subDetails,'Name':studentInfo[0].Name,'RollNo':studentInfo[0].RollNo})



# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_makeup_summary_info(request):
#     print('SupGradesProcessing')
#     makeupSummaryStats = MakeupSummaryStats.objects.all()  
#     summaryStats = {}
#     years = ['II B.Tech.','III B.Tech.','IV B.Tech.']
#     programmeDetails = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
#     deptDetails = [ prog.Specialization for prog in programmeDetails]
    
#     for dept in range(1,9):
#         deptSummaryStats = {}
#         for year in range(2,5):
#             deptYearSummaryStats = makeupSummaryStats.filter(Dept=dept).filter(BYear=year)
#             deptSummaryStats[years[year-2]] = deptYearSummaryStats
#         summaryStats[deptDetails[dept-1]] = deptSummaryStats
#     return render(request, 'SupExamDB/SupBTGradeProcessing.html',{'summaryStats': summaryStats,})

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_regular_registration_upload(request):
#     if(request.method=='POST'):
#         regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
#         regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode) for row in regIDs]
#         form = RegistrationsUploadForm(regIDs, request.POST,request.FILES)
#         if(form.is_valid()):
#             print(form.cleaned_data['regID'])
#             (ayear,asem,byear,bsem,dept,mode) = regIDs[int(form.cleaned_data['regID'])]
#             if(((byear==1) and (dept>=9)) or ((byear>1) and (dept<=8))):
#                 file = form.cleaned_data['file']
#                 data = bytes()
#                 for chunk in file.chunks():
#                     data += chunk
#                 dataset = XLSX().create_dataset(data)
#                 #print('IS VALID')
#                 # depts = {'BTE':1,'CHE':2,'CE':3,'CSE':4,'EEE':5,'ECE':6,'ME':7,'MME':8,'CHEMISTRY':9,'PHYSICS':10}
#                 # years = {'I':1,'II':2,'III':3,'IV':4}
#                 # sems = {'I':1,'II':2}
#                 # ayear = int(values[3])
#                 # asem = sems[values[4]]
#                 # byear = years[values[1]]
#                 # bsem = sems[values[2]]
#                 # dept = depts[values[0]]
#                 #print(dataset[0:10])
#                 #print(str(ayear) + ':' + str(asem) + ':' + str(byear)+':' + str(bsem))
#                 mode = 1 # hard-coded to study mode as these are regular registrations
#                 newDataset= Dataset()
#                 newDataset.headers = ['RegNo', 'SubCode', 'AYear', 'ASem', 'OfferedYear', 'Dept', 'BYear', 'Regulation','BSem', 'Mode']
#                 for i in range(len(dataset)):
#                     row = dataset[i]
#                     newRow = (row[0],str(row[1]),ayear,asem, ayear, int(dept), byear,row[2],bsem,mode)
#                     newDataset.append(newRow)
#                 print(newDataset[0:10])
#                 registration_resource = StudentRegistrationsResource()
#                 result = registration_resource.import_data(newDataset, dry_run=True)
#                 #df = pd.read_excel(file)
#                 if not result.has_errors():
#                     registration_resource.import_data(newDataset, dry_run=False)
#                     return(render(request,'SupExamDBRegistrations/BTRegistrationUploadSuccess.html'))
#                 else:
#                     errors = result.row_errors()
#                     print(errors[0][1][0].error)
#                     indices = set([i for i in range(len(newDataset))])    
#                     errorIndices = set([i[0]-1 for i in errors])
#                     print(errors[0][0])
#                     cleanIndices = indices.difference(errorIndices)
#                     cleanDataset = Dataset()
#                     for i in list(cleanIndices):
#                         cleanDataset.append(newDataset[i])
#                     cleanDataset.headers = newDataset.headers
                    
#                     result1 = registration_resource.import_data(cleanDataset, dry_run=True)
#                     if not result1.has_errors():
#                         registration_resource.import_data(cleanDataset, dry_run=False)
#                     else:
#                         print('Something went wrong in plain import')
#                     for i in errorIndices:
#                         updateRow = newDataset[i]
                    
#                     errorData = Dataset()
#                     for i in list(errorIndices):
#                         errorData.append(newDataset[i])
#                     registrationRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7],errorData[i][8],errorData[i][9] ) for i in range(len(errorData))]
                        

#                     #updateForm = FacultyUpdateForm(Options=facultyRows)
#                     request.session['registrationRows'] = registrationRows 
                    
#                     return HttpResponseRedirect(reverse('SupBTRegistrationUploadErrorHandler' ))
#         else:
#             print(form.errors)
#             for row in form.fields.values(): print(row)
#     else:
#         regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
#         regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode) for row in regIDs]
#         form = RegistrationsUploadForm(Options=regIDs)
#     return(render(request, 'SupExamDBRegistrations/BTRegularRegistrationUpload.html',{'form':form }))

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def btech_regular_registration_upload_error_handler(request):
#     registrationRows = request.session.get('registrationRows')
#     for row in registrationRows:
#         print(row[0])
#     if(request.method=='POST'):
#         form = StudentRegistrationUpdateForm(registrationRows,request.POST)
#         if(form.is_valid()):
#             for cIndex, fRow in enumerate(registrationRows):
#                 if(form.cleaned_data.get('Check'+str(fRow[0]))):
#                     StudentRegistrations.objects.filter(RegNo=fRow[0], SubCode=fRow[1],AYear=fRow[2],ASem=fRow[3],OfferedYear=fRow[4],Dept=fRow[5],BYear=fRow[6],Regulation=fRow[7],BSem=fRow[8]).update(RegNo=fRow[0], SubCode=fRow[1],AYear=fRow[2],ASem=fRow[3],OfferedYear=fRow[4],Dept=fRow[5],BYear=fRow[6],Regulation=fRow[7],BSem=fRow[8])
#             return render(request, 'SupExamDBRegistrations/BTRegistrationUploadSuccess.html')
#     else:
#         form = StudentRegistrationUpdateForm(Options=registrationRows)

#     return(render(request, 'SupExamDBRegistrations/BTRegistrationUploadErrorHandler.html',{'form':form}))
