from unicodedata import name
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from SupExamDBRegistrations.forms import BacklogRegistrationForm, GradesUploadForm, RegistrationsEventForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, GradesUpdateForm,\
         GradesFinalizeForm, GradeChallengeForm
from SupExamDBRegistrations.models import RegistrationStatus, Regulation, StudentBacklogs, StudentGrades, StudentInfo, \
    StudentMakeupBacklogsVsRegistrations, StudentRegistrations, Subjects, Subjects_Staging, \
        DroppedRegularCourses, StudentGrades_StagingResource, StudentGrades_Staging, GradeChallengeResource
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX
import psycopg2

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def upload_grades(request):
    if request.method == 'POST':
        form = GradesUploadForm(request.POST, request.FILES)
        if form.is_valid():
            regevent = form.cleaned_data['regID']
            strs = regevent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            newDataset= Dataset()
            errorDataset = Dataset()#To store subjects rows which are not related to present registration event
            errorDataset.headers = ['RegNo', 'SubCode', 'Grade', 'AYear', 'ASem','OfferedYear', 'Dept', 'AttGrade','RegId']
            newDataset.headers = ['RegId', 'RegEventId', 'Regulation', 'Grade', 'AttGrade']
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            for i in range(len(dataset)):
                row = dataset[i]
                if((row[3],row[4],row[6])==(ayear,asem,dept)):
                    regs = StudentRegistrations.objects.filter(RegNo=int(row[0]),RegEventId=currentRegEventId)
                    # print(regs)
                    regid = ''
                    for reg in regs:
                        sub = Subjects.objects.get(id=reg.sub_id)
                        # print(sub.SubCode, row[1], sub.SubCode==row[1])
                        if sub.SubCode == row[1]:
                            regid = reg.id
                            break
                    if regid != '':
                        newRow = (regid, currentRegEventId, regulation, row[2], row[7])
                        newDataset.append(newRow)
                    else:
                        # print("here")
                        newRow = (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],'')
                        errorDataset.append(newRow)
                else:
                    newRow = (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],'')
                    errorDataset.append(newRow)
            # print(errorDataset)
            Grades_resource = StudentGrades_StagingResource()
            result = Grades_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                Grades_resource.import_data(newDataset, dry_run=False)
                if(len(errorDataset)!=0):
                    gradesErrRows = [ (errorDataset[i][0],errorDataset[i][1],errorDataset[i][2],errorDataset[i][3],\
                        errorDataset[i][4],errorDataset[i][5],errorDataset[i][6],errorDataset[i][7], errorDataset[i][8] ) for i in range(len(errorDataset))]
                    # print(gradesErrRows)
                    request.session['gradesErrRows'] = gradesErrRows
                    request.session['currentRegEventId'] = currentRegEventId 
                    return HttpResponseRedirect(reverse('GradesUploadErrorHandler'))
                return(render(request,'SupExamDBRegistrations/GradesUploadSuccess.html'))
            else:
                errors = result.row_errors()
                # print(errors[0][1][0].error)
                indices = set([i for i in range(len(newDataset))])    
                errorIndices = set([i[0]-1 for i in errors])
                # print(errorIndices)
                cleanIndices = indices.difference(errorIndices)
                # print(cleanIndices)
                cleanDataset = Dataset()
                for i in list(cleanIndices):
                    cleanDataset.append(newDataset[i])
                cleanDataset.headers = newDataset.headers
                
                result1 = Grades_resource.import_data(cleanDataset, dry_run=True)
                if not result1.has_errors():
                    Grades_resource.import_data(cleanDataset, dry_run=False)
                else:
                    print('Something went wrong in plain import')
                errorData = Dataset()
                errorData.headers = errorDataset.headers
                for i in list(errorIndices):
                    stud_reg = StudentRegistrations.objects.get(id=newDataset[i][0])
                    sub = Subjects.objects.get(id=stud_reg.sub_id)
                    regEvent = RegistrationStatus.objects.get(id=sub.RegEventId)
                    newRow = (stud_reg.RegNo,sub.SubCode,newDataset[i][3],ayear,asem,regEvent.AYear,dept,newDataset[i][4],newDataset[i][0])
                    errorData.append(newRow)
                for i in errorDataset:
                    errorData.append(i)
                gradesErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],\
                            errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7], errorData[i][8]) for i in range(len(errorData))]
                request.session['gradesErrRows'] = gradesErrRows
                request.session['currentRegEventId'] = currentRegEventId 
                return HttpResponseRedirect(reverse('GradesUploadErrorHandler'))
    else:
        form = GradesUploadForm()
    return render(request, 'SupExamDBRegistrations/GradesUpload.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def grades_upload_error_handler(request):
    gradesRows = request.session.get('gradesErrRows')
    currentRegEventId = request.session.get('currentRegEventId')
    if(request.method=='POST'):
        form = GradesUpdateForm(gradesRows,request.POST)
        if(form.is_valid()):
            regevent = RegistrationStatus.objects.get(id=currentRegEventId)
            for cIndex, fRow in enumerate(gradesRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    if((fRow[8])!=''):
                        StudentGrades_Staging.objects.filter(RegId=fRow[8]).update(Regulation=regevent.Regulation,\
                            Grade=fRow[2],AttGrade=fRow[7])
            return render(request, 'SupExamDBRegistrations/GradesUploadSuccess.html')
    else:
        form = GradesUpdateForm(Options=gradesRows)
    return(render(request, 'SupExamDBRegistrations/GradesUploadErrorHandler.html',{'form':form}))


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def grades_finalize(request):
    if request.method == 'POST':
        form = GradesFinalizeForm(request.POST)
        if form.is_valid():
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
                regulation = int(strs[5])
                mode = strs[6]
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                grades = StudentGrades_Staging.objects.filter(RegEventId=currentRegEventId)
                for g in grades:
                    gr = StudentGrades(RegId=g.RegId, Regulation=g.Regulation, RegEventId=g.RegEventId, Grade=g.Grade, AttGrade=g.AttGrade)
                    gr.save()
                RefreshMaterializedViews()
                return render(request, 'SupExamDBRegistrations/GradesFinalizeSuccess.html')
    else:
        form = GradesFinalizeForm()
    return render(request, 'SupExamDBRegistrations/GradesFinalize.html', {'form':form})

def RefreshMaterializedViews():
    conn = psycopg2.connect(
    host="localhost",
    database="public",
    # name="public",
    user="postgres",
    password="postgresql")
    cursor = conn.cursor()

    try:
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"StudentGradePointsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"StudentBacklogsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"StudentMakeupBacklogsMV\" WITH DATA;")
    finally:
        cursor.close()
        conn.commit()

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def grade_challenge(request):
    if request.method == 'POST':
        form = GradeChallengeForm(request.POST, request.FILES)
        if form.is_valid():
            regevent = form.cleaned_data['regEvent']
            strs = regevent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            newDataset= Dataset()
            errorGradeChallenge = []
            errorGrades = []
            errrorSameGrades = [] #if previous and updated grades are same
            newDataset.headers = ['RegId', 'PreviousGrade', 'UpdatedGrade']
            currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            for i in range(len(dataset)):
                row = dataset[i]
                if((row[3],row[4],row[6])==(ayear,asem,dept)):
                    regs = StudentRegistrations.objects.filter(RegNo=row[0],RegEventId=currentRegEventId)
                    regid = ''
                    for reg in regs:
                        sub = Subjects.objects.get(id=reg.sub_id)
                        if sub.SubCode == row[1]:
                            regid = reg.id
                            break
                    if regid != '':
                        if StudentGrades_Staging.objects.filter(RegId=regid, RegEventId=currentRegEventId, Regulation=regulation,\
                             Grade=row[2], AttGrade=row[7]).exists():
                            if row[2]==row[8]:
                                errrorSameGrades.append(row)
                            else:
                                newRow = (regid, row[2], row[8])
                                newDataset.append(newRow)
                                grade = StudentGrades_Staging.objects.get(RegId=regid, RegEventId=currentRegEventId, Regulation=regulation,\
                                    Grade=row[2], AttGrade=row[7])
                                grade.Grade = row[8]
                                grade.save() 
                        else:
                            errorGrades.append(row)
                    else:
                        errorGrades.append(row)
                else:
                    errorGrades.append(row)
            GradeChallenge_resource = GradeChallengeResource()
            result = GradeChallenge_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                GradeChallenge_resource.import_data(newDataset, dry_run=False)
                # if(len(errorGrades)!=0):
                    # gradesErrRows = [ (errorGrades[i][0],errorGrades[i][1],errorGrades[i][2],errorGrades[i][3],\
                    #     errorGrades[i][4],errorGrades[i][5],errorGrades[i][6],errorGrades[i][7], errorGrades[i][8],errorGrades[i][9] ) \
                    # #         for i in range(len(errorGrades))]
                    # request.session['gradesErrRows'] = gradesErrRows
                    # request.session['currentRegEventId'] = currentRegEventId 
                    # return HttpResponseRedirect(reverse('GradesUploadErrorHandler'))
                    # return render(request, 'SupExamDBRegistrations/GradeChallengeSucces.html', {'errorGrades':errorGrades})
            else:
                errors = result.row_errors()
                # print(errors[0][1][0].error)
                indices = set([i for i in range(len(newDataset))])    
                errorIndices = set([i[0]-1 for i in errors])
                cleanIndices = indices.difference(errorIndices)
                cleanDataset = Dataset()
                for i in list(cleanIndices):
                    cleanDataset.append(newDataset[i])
                cleanDataset.headers = newDataset.headers
                result1 = GradeChallenge_resource.import_data(cleanDataset, dry_run=True)
                if not result1.has_errors():
                    GradeChallenge_resource.import_data(cleanDataset, dry_run=False)
                else:
                    print('Something went wrong in plain import')
                for i in list(errorIndices):
                    stud_grade = StudentGrades_Staging.objects.get(RegId=newDataset[i][0])
                    stud_reg = StudentRegistrations.objects.get(id=newDataset[i][0])
                    sub = Subjects.objects.get(id=stud_reg.sub_id)
                    regEvent = RegistrationStatus.objects.get(id=sub.RegEventId)
                    newRow = (stud_reg.RegNo,sub.SubCode,newDataset[i][1],ayear,asem,regEvent.AYear,dept,stud_grade.AttGrade,newDataset[i][2])
                    errorGradeChallenge.append(newRow)
            return render(request, 'SupExamDBRegistrations/GradeChallengeSuccess.html', {'errorGrades':errorGrades,\
                'errorGradeChallenge':errorGradeChallenge, 'errorSameGrades':errrorSameGrades})
        # return render(request, 'SupExamDBRegistrations/GradeChallengeSuccess.html')
    else:
        form = GradeChallengeForm()
    return render(request, 'SupExamDBRegistrations/GradeChallenge.html', {'form':form})

