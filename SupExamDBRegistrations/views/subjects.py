
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from SupExamDBRegistrations.forms import BacklogRegistrationForm, RegistrationsEventForm, RegistrationsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm
from SupExamDBRegistrations.models import RegistrationStatus, StudentBacklogs, StudentInfo, StudentRegistrations, SubjectStagingResource, Subjects, Subjects_Staging
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def subject_home(request):
    return render(request, 'SupExamDBRegistrations/subjecthome.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def subject_upload(request):
    if(request.method=='POST'):
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode) for row in regIDs]
        form = RegistrationsUploadForm(regIDs, request.POST,request.FILES)
        if(form.is_valid()):
            print(form.cleaned_data['regID'])
            (ayear,asem,byear,bsem,dept,mode) = regIDs[int(form.cleaned_data['regID'])]
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            print('IS VALID')
            print(dataset[0:10])
            print(str(ayear) + ':' + str(asem) + ':' + str(byear)+':' + str(bsem))
            mode = 1 # hard-coded to study mode as these are regular registrations
            newDataset= Dataset()
            newDataset.headers = ['SubCode', 'SubName', 'BYear', 'BSem', 'Dept','OfferedYear', 'Regulation','Creditable', 'Credits','Type','Category']
            for i in range(len(dataset)):
                row = dataset[i]
                newRow = (row[0],row[1],byear,bsem,dept,ayear,row[3],row[2],row[4],row[5],row[6])
                newDataset.append(newRow)
            print(newDataset[0:10])
            Subject_resource = SubjectStagingResource()
            result = Subject_resource.import_data(newDataset, dry_run=True)
            #df = pd.read_excel(file)
            if not result.has_errors():
                
                    Subject_resource.import_data(newDataset, dry_run=False)
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
                for i in errorIndices:
                    updateRow = newDataset[i]
                   
                errorData = Dataset()
                for i in list(errorIndices):
                    errorData.append(newDataset[i])
                registrationRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7],errorData[i][8],errorData[i][9], errorData[i][10] ) for i in range(len(errorData))]
                    

                #updateForm = FacultyUpdateForm(Options=facultyRows)
                request.session['registrationRows'] = registrationRows 
                
                return HttpResponseRedirect(reverse('SupBTSubjectsUploadErrorHandler' ))
        else:
            print(form.errors)
            for row in form.fields.values(): print(row)
    else:
        regIDs = RegistrationStatus.objects.filter(Status=1,Mode='R')
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode) for row in regIDs]
        form = RegistrationsUploadForm(Options=regIDs)
    return (render(request, 'SupExamDBRegistrations/BTSubjectsUpload.html', {'form':form}))

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def subject_upload_error_handler(request):
    subjectRows = request.session.get('registrationRows')
    for row in subjectRows:
        print(row[0])
    if(request.method=='POST'):
        form = StudentRegistrationUpdateForm(subjectRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(subjectRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    StudentRegistrations.objects.filter(SubCode=fRow[0],Dept = fRow[4], OfferedYear=fRow[5],Regulation=fRow[6]).update(SubName=fRow[1],Credits=fRow[8],Creditable=fRow[7],Type=fRow[9], Category=fRow[10])
            return render(request, 'SupExamDBRegistrations/BTSubjectsUploadSuccess.html')
    else:
        form = StudentRegistrationUpdateForm(Options=subjectRows)

    return(render(request, 'SupExamDBRegistrations/BTSubjectsUploadErrorHandler.html',{'form':form}))

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
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
            strs = form.cleaned_data['regID'].split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            mode = strs[5]
            subjects = []
            if(mode=='R'):
                subjects = Subjects_Staging.objects.filter(OfferedYear=ayear,BSem=bsem,Dept=dept,BYear=byear)
            else:
                subjects = Subjects.objects.filter(OfferedYear=ayear,BSem=bsem,Dept=dept,BYear=byear)
            return render(request, 'SupExamDBRegistrations/BTSubjectsUploadStatus.html',{'subjects':subjects.values(),'form':form})
        else:
            print('Invalid')
    else:
        form = RegistrationsEventForm()
    return render(request, 'SupExamDBRegistrations/BTSubjectsUploadStatus.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
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
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                strs = form.cleaned_data['regID'].split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                mode = strs[5]
                if(mode=='R'): # deleting is only valid for regular registrations, the other case is not even possible
                    subjects = []
                    deletedSubjects = []
                    for sub in form.myFields:
                        if(form.cleaned_data['Check'+sub[0]]==True):
                            subject = Subjects_Staging.objects.filter(OfferedYear=ayear,BSem=bsem,Dept=dept,BYear=byear,SubCode=sub[0],Regulation=sub[4])
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
@user_passes_test(is_Superintendent)
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