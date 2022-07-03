
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from SupExamDB.views import is_Co_ordinator
from SupExamDBRegistrations.forms import RegistrationsEventForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm
from SupExamDBRegistrations.models import RegistrationStatus, Subjects, Subjects_Staging
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from SupExamDBRegistrations.resources import SubjectStagingResource
from SupExamDBRegistrations.user_access_test import subject_access

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_home(request):
    return render(request, 'SupExamDBRegistrations/subjecthome.html')

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_upload(request):
    if(request.method=='POST'):
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs1 = RegistrationStatus.objects.filter(Status=1,Mode='D')#For Dropped regular courses, upload subjects 
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        regIDs += [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs1]
        form = SubjectsUploadForm(regIDs, request.POST,request.FILES)
        if(form.is_valid()):
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,byear,bsem,dept,mode,regulation) = regIDs[int(form.cleaned_data['regID'])]
                file = form.cleaned_data['file']
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                newDataset= Dataset()
                errorDataset = Dataset()#To store subjects rows which are not related to present registration event
                errorDataset.headers = ['SubCode', 'SubName', 'BYear', 'BSem', 'Dept','OfferedYear', 'Regulation',\
                    'Creditable', 'Credits','Type','Category','OfferedBy']
                newDataset.headers = ['SubCode', 'SubName', 'Creditable', 'Credits','OfferedBy', 'Type', 'Category', 'RegEventId']
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                for i in range(len(dataset)):
                    row = dataset[i]
                    if((row[3],row[4],row[5],row[6],row[9])==(byear,bsem,dept,ayear,regulation)):
                        print("in if",row[0])
                        newRow = (row[0],row[1],row[10],row[2],row[11],row[7],row[8],currentRegEventId)
                        newDataset.append(newRow)
                    else:
                        print("in else",row[0])
                        newRow = (row[0],row[1],row[3],row[4],row[5],row[6],row[9],row[10],row[2],row[7],row[8],row[11])
                        errorDataset.append(newRow)
                Subject_resource = SubjectStagingResource()
                result = Subject_resource.import_data(newDataset, dry_run=True)
                if not result.has_errors():
                    print('hiiiii   ')
                    Subject_resource.import_data(newDataset, dry_run=False)
                    if(len(errorDataset)!=0):
                        subErrRows = [ (errorDataset[i][0],errorDataset[i][1],errorDataset[i][2],errorDataset[i][3],\
                            errorDataset[i][4],errorDataset[i][5],errorDataset[i][6],errorDataset[i][7],errorDataset[i][8],\
                            errorDataset[i][9], errorDataset[i][10],errorDataset[i][11] ) for i in range(len(errorDataset))]
                        request.session['subErrRows'] = subErrRows
                        request.session['currentRegEventId'] = currentRegEventId 
                        return HttpResponseRedirect(reverse('SupBTSubjectsUploadErrorHandler' ))
                    return(render(request,'SupExamDBRegistrations/BTSubjectsUploadSuccess.html'))
                else:
                    errors = result.row_errors()
                    print("errors - ",errors[0][1][0].error)
                    indices = set([i for i in range(len(newDataset))])    
                    errorIndices = set([i[0]-1 for i in errors])
                    cleanIndices = indices.difference(errorIndices)
                    cleanDataset = Dataset()
                    for i in list(cleanIndices):
                        cleanDataset.append(newDataset[i])
                    cleanDataset.headers = newDataset.headers
                
                    result1 = Subject_resource.import_data(cleanDataset, dry_run=True)
                    if not result1.has_errors():
                        Subject_resource.import_data(cleanDataset, dry_run=False)
                    else:
                        print('Something went wrong in plain import')
                    errorData = Dataset()
                    for i in list(errorIndices):
                        newRow = (newDataset[i][0],newDataset[i][1],byear,bsem,dept,ayear,regulation,newDataset[i][2],\
                            newDataset[i][3],newDataset[i][5],newDataset[i][6],newDataset[i][4])
                        errorData.append(newRow)
                    for i in errorDataset:
                        errorData.append(i)
                    subErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],\
                    errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7],errorData[i][8],\
                        errorData[i][9], errorData[i][10],errorData[i][11] ) for i in range(len(errorData))]
                    request.session['subErrRows'] = subErrRows
                    request.session['currentRegEventId'] = currentRegEventId                
                    return HttpResponseRedirect(reverse('SupBTSubjectsUploadErrorHandler'))

        else:
            print(form.errors)
            for row in form.fields.values(): print(row)
    else:
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs1 = RegistrationStatus.objects.filter(Status=1,Mode='D')#For Dropped regular courses, upload subjects 
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        regIDs += [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs1]
        form = SubjectsUploadForm(Options=regIDs)
    return (render(request, 'SupExamDBRegistrations/BTSubjectsUpload.html', {'form':form}))

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_upload_error_handler(request):
    subjectRows = request.session.get('subErrRows')
    currentRegEventId = request.session.get('currentRegEventId')
    for row in subjectRows:
        print(row[0])
    if(request.method=='POST'):
        form = StudentRegistrationUpdateForm(subjectRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(subjectRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    Subjects_Staging.objects.filter(SubCode=fRow[0],RegEventId=currentRegEventId).update(SubName=fRow[1],\
                        Credits=fRow[8],Creditable=fRow[7],Type=fRow[9],Category=fRow[10],OfferedBy=fRow[11])
            return render(request, 'SupExamDBRegistrations/BTSubjectsUploadSuccess.html')
    else:
        form = StudentRegistrationUpdateForm(Options=subjectRows)
    return(render(request, 'SupExamDBRegistrations/BTSubjectsUploadErrorHandler.html',{'form':form}))

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_upload_status(request):
    if(request.method=='POST'):
        form = RegistrationsEventForm(request.POST)
        print(request.POST)
        print(form.errors)
        print(form.non_field_errors)
        if(form.is_valid()):
            print('valid form')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            print(form.cleaned_data['regID'])
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
                subjects = []
                if(mode=='R' or mode=='D'):
                    subjects = Subjects_Staging.objects.filter(RegEventId=currentRegEventId)
                else:
                    subjects = Subjects.objects.filter(RegEventId=currentRegEventId)
                return render(request, 'SupExamDBRegistrations/BTSubjectsUploadStatus.html',{'subjects':subjects.values(),'form':form})
            return render(request, 'SupExamDBRegistrations/BTSubjectsUploadStatus.html',{'form':form})
            
            
        else:
            print('Invalid')
    else:
        form = RegistrationsEventForm()
    return render(request, 'SupExamDBRegistrations/BTSubjectsUploadStatus.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_delete(request):
    if(request.method=='POST'):
        form = SubjectDeletionForm(request.POST)
        if('regID' in request.POST.keys()):
            print(request.POST)
            if(form.is_valid()):
                print('Valid')
                depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
                years = {1:'I',2:'II',3:'III',4:'IV'}
                deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
                print(deptDict)
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
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
                if(mode=='R'): # deleting is only valid for regular registrations, the other case is not even possible
                    subjects = []
                    deletedSubjects = []
                    for sub in form.myFields:
                        if(form.cleaned_data['Check'+sub[0]]==True):
                            subject = Subjects_Staging.objects.filter(SubCode=sub[0],RegEventId=currentRegEventId)
                            subject.delete()
                            deletedSubjects.append(sub[0]+':' + str(sub[4]))
                        else:
                            subjects.append(sub[0])
                    if(len(deletedSubjects)!=0):
                        msg = '<p> Deletion of subjects completed successfully for registration event'+ form.cleaned_data['regID'] 
                        
                        msg = msg + '.</p> <p> ' 
                        for dsub in deletedSubjects:
                            msg = msg + dsub + ',' 
                        msg = msg  + ' are the deleted subject ids. </p>'
                        return(render(request,'SupExamDBRegistrations/BTSubjectsDeleteSuccess.html',{'msg': msg}))
            else:
                print('Invalid')
                print(form.errors)
                
    else:
        form = SubjectDeletionForm()
    return render(request, 'SupExamDBRegistrations/BTSubjectsDelete.html',{'form':form})
@login_required(login_url="/login/")
@user_passes_test(is_Co_ordinator)
def subject_delete_handler(request,event):
    if(request.method=='POST'):
        form = SubjectDeletionForm(request.POST)
    else:
        form = SubjectDeletionForm()
    return render(request, 'SupExamDBRegistrations/BTSubjectsDeletionHandler.html',{'form':form })

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def subject_delete_success(request):
    if(request.method=='POST'):
        form = SubjectDeletionForm(request.POST)
    else:
        form = SubjectDeletionForm()
    return render(request, 'SupExamDBRegistrations/BTSubjectsDeletionHandler.html',{'form':form })


@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_finalize(request):
    if(request.method=='POST'):
        form = SubjectFinalizeEventForm(request.POST)
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
                regulation = int(strs[5])
                mode = strs[6]
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                subjects = []
                subjects = Subjects_Staging.objects.filter(RegEventId=currentRegEventId)
                for sub in subjects:
                   s=Subjects(SubCode=sub.SubCode,SubName=sub.SubName,Creditable=sub.Creditable,Credits=sub.Credits,\
                           Type=sub.Type,Category=sub.Category,RegEventId=sub.RegEventId)
                   s.save() 
                return render(request, 'SupExamDBRegistrations/BTSubjectFinalizeSuccess.html')
        else:
            print('Invalid')
    else:
        form = SubjectFinalizeEventForm()
    return render(request, 'SupExamDBRegistrations/BTSubjectFinalize.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def open_subject_upload(request):
    if(request.method=='POST'):
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs1 = RegistrationStatus.objects.filter(Status=1,Mode='D')#For Dropped regular courses, upload subjects 
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        regIDs += [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs1]
        form = SubjectsUploadForm(regIDs, request.POST,request.FILES)
        if(form.is_valid()):
            print(form.cleaned_data['regID'])
            if(form.cleaned_data['regID']!='--Choose Event--'):
                (ayear,asem,byear,bsem,dept,mode,regulation) = regIDs[int(form.cleaned_data['regID'])]
                file = form.cleaned_data['file']
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                # mode = 1 # hard-coded to study mode as these are regular registrations
                newDataset= Dataset()
                errorDataset = Dataset()#To store subjects rows which are not related to present registration event
                errorDataset.headers = ['SubCode', 'SubName', 'BYear', 'BSem', 'Dept','OfferedYear', 'Regulation',\
                    'Creditable', 'Credits','Type','Category']
                newDataset.headers = ['SubCode', 'SubName', 'Creditable', 'Credits', 'Type', 'Category', 'RegEventId']
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                for i in range(len(dataset)):
                    row = dataset[i]
                    if((row[3],row[4],row[5],row[6],row[9])==(byear,bsem,dept,ayear,regulation) and row[8]=='OEC'):
                        newRow = (row[0],row[1],row[10],row[2],row[7],row[8],currentRegEventId)
                        newDataset.append(newRow)
                    else:
                        newRow = (row[0],row[1],row[3],row[4],row[5],row[6],row[9],row[10],row[2],row[7],row[8])
                        errorDataset.append(newRow)
                Subject_resource = SubjectStagingResource()
                result = Subject_resource.import_data(newDataset, dry_run=True)
                if not result.has_errors():
                    Subject_resource.import_data(newDataset, dry_run=False)
                    if(errorDataset!=None):
                        subErrRows = [ (errorDataset[i][0],errorDataset[i][1],errorDataset[i][2],errorDataset[i][3],\
                            errorDataset[i][4],errorDataset[i][5],errorDataset[i][6],errorDataset[i][7],errorDataset[i][8],\
                            errorDataset[i][9], errorDataset[i][10] ) for i in range(len(errorDataset))]
                        request.session['subErrRows'] = subErrRows
                        request.session['currentRegEventId'] = currentRegEventId 
                        return HttpResponseRedirect(reverse('SupBTSubjectsUploadErrorHandler' ))
                    return(render(request,'SupExamDBRegistrations/BTSubjectsUploadSuccess.html'))
                else:
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
                
                    result1 = Subject_resource.import_data(cleanDataset, dry_run=True)
                    if not result1.has_errors():
                        Subject_resource.import_data(cleanDataset, dry_run=False)
                    else:
                        print('Something went wrong in plain import')
                    errorData = Dataset()
                    for i in list(errorIndices):
                        newRow = (newDataset[i][0],newDataset[i][1],byear,bsem,dept,ayear,regulation,newDataset[i][2],\
                            newDataset[i][3],newDataset[i][4],newDataset[i][5])
                        errorData.append(newRow)
                    for i in errorDataset:
                        errorData.append(i)
                    subErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],\
                    errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7],errorData[i][8],\
                        errorData[i][9], errorData[i][10] ) for i in range(len(errorData))]
                    request.session['subErrRows'] = subErrRows
                    request.session['currentRegEventId'] = currentRegEventId                
                    return HttpResponseRedirect(reverse('SupBTSubjectsUploadErrorHandler' ))

        else:
            print(form.errors)
            for row in form.fields.values(): print(row)
    else:
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs1 = RegistrationStatus.objects.filter(Status=1,Mode='D')#For Dropped regular courses, upload subjects 
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
        regIDs += [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs1]
        form = SubjectsUploadForm(Options=regIDs)
    return (render(request, 'SupExamDBRegistrations/BTSubjectsUpload.html', {'form':form}))