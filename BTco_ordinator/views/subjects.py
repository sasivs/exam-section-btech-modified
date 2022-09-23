
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from BTco_ordinator.forms import RegistrationsEventForm, SubjectsUploadForm, StudentRegistrationUpdateForm, \
    SubjectDeletionForm, SubjectFinalizeEventForm
from BTco_ordinator.models import BTSubjects_Staging, BTSubjects
from BTco_ordinator.resources import SubjectStagingResource
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTHOD, BTMarksDistribution, BTCycleCoordinator
from BThod.models import BTCoordinator
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from BTsuperintendent.user_access_test import subject_access, subject_home_access, is_Superintendent


@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = []
    msg = ''
    if 'Cycle-Co-ordinator' in groups:
        coordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1, Dept=coordinator.Cycle, Mode='R')
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if(request.method=='POST'):
        form = SubjectsUploadForm(regIDs, request.POST,request.FILES)
        if request.POST.get('upload_file_submit'):
            (ayear,asem,byear,bsem,dept,mode,regulation) = regIDs[int(request.POST['regID'])]
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear, BYear=byear, ASem=asem, BSem=bsem, Dept=dept, Mode=mode, Regulation=regulation).first().id
            if(form.is_valid()):
                if(form.cleaned_data['regID']!='--Choose Event--'):
                    file = form.cleaned_data['file']
                    data = bytes()
                    for chunk in file.chunks():
                        data += chunk
                    dataset = XLSX().create_dataset(data)
                    newDataset= Dataset()
                    errorDataset = Dataset()#To store subjects rows which are not related to present registration event
                    errorDataset.headers = ['SubCode', 'SubName', 'BYear', 'BSem', 'Dept','OfferedYear', 'Regulation',\
                        'Creditable', 'Credits','Type','Category', 'OfferedBy']
                    newDataset.headers = ['SubCode', 'SubName', 'Creditable', 'Credits', 'Type', 'Category', 'RegEventId', 'OfferedBy', \
                        'DistributionRatio', 'MarkDistribution']
                    currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation)
                    currentRegEventId = currentRegEventId[0].id
                    marks_distribution = BTMarksDistribution.objects.all()
                    for i in range(len(dataset)):
                        row = dataset[i]
                        if((row[2],row[3],row[4],row[5],row[6])==(byear,bsem,dept,ayear,regulation)):
                            newRow = (row[0],row[1],row[7],row[8],row[9],row[10],currentRegEventId, row[11], '', '')
                            newDataset.append(newRow)
                        else:
                            newRow = (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11])
                            errorDataset.append(newRow)
                    request.session['newDataset'] = list(newDataset)
                    request.session['currentRegEventId'] = currentRegEventId              
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'errorRows':errorDataset, \
                    'validRows':newDataset, 'marks_distribution':marks_distribution})
        elif request.POST.get('mark_dis_submit'):
            newDataset = Dataset()
            newDataset.headers = ['SubCode', 'SubName', 'Creditable', 'Credits', 'Type', 'Category', 'RegEventId', 'OfferedBy', \
                    'DistributionRatio', 'MarkDistribution']
            errorRows = []
            for row in request.session.get('newDataset'):
                row[8] = request.POST.get('ratio_distribution_'+str(row[0])).strip()
                row[9] = int(request.POST.get('mark_distribution_'+str(row[0])))
                newRow = (row[0],row[1],row[2],row[3],row[4],row[5],row[6], row[7], row[8], row[9])
                mark_distribution = BTMarksDistribution.objects.filter(id=row[9]).first()
                if len(mark_distribution.Distribution.split(',')) != len(row[8].split(':')):
                    errorRows.append(newRow)
                else:
                    newDataset.append(newRow)
            Subject_resource = SubjectStagingResource()
            result = Subject_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                Subject_resource.import_data(newDataset, dry_run=False)
            else:
                errors = result.row_errors()
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
                    newRow = (newDataset[i][0],newDataset[i][1],newDataset[i][2],\
                        newDataset[i][3],newDataset[i][4],newDataset[i][5],newDataset[i][6], newDataset[i][7], newDataset[i][8], newDataset[i][9])
                    errorData.append(newRow)
                subErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],\
                errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7], errorData[i][8], errorData[i][9]) for i in range(len(errorData))]
                request.session['subErrRows'] = subErrRows
                request.session['errorRows'] = errorRows
                # request.session['currentRegEventId'] = currentRegEventId              
                return HttpResponseRedirect(reverse('BTSupBTSubjectsUploadErrorHandler'))
            if errorRows:
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'errorRows1':errorRows})
            msg = 'Subjects Uploaded successfully.'

    else:
        form = SubjectsUploadForm(Options=regIDs)
    return (render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'msg':msg}))

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_upload_error_handler(request):
    subjectRows = request.session.get('subErrRows')
    errorRows = request.session.get('errorRows')
    currentRegEventId = request.session.get('currentRegEventId')
    if(request.method=='POST'):
        form = StudentRegistrationUpdateForm(subjectRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(subjectRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    BTSubjects_Staging.objects.filter(SubCode=fRow[0],RegEventId=currentRegEventId).update(SubName=fRow[1],\
                        Creditable=fRow[2],Credits=fRow[3],Type=fRow[4],Category=fRow[5],OfferedBy=fRow[7],\
                             DistributionRatio=fRow[8], MarkDistribution=fRow[9])
            return render(request, 'BTco_ordinator/BTSubjectsUploadSuccess.html')
    else:
        form = StudentRegistrationUpdateForm(Options=subjectRows)
    return(render(request, 'BTco_ordinator/BTSubjectsUploadErrorHandler.html',{'form':form, 'errorRows':errorRows}))

@login_required(login_url="/login/")
@user_passes_test(subject_home_access)
def subject_upload_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='R')
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=co_ordinator.BYear, Dept=co_ordinator.Dept, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        co_ordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Cycle, Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if(request.method=='POST'):
        form = RegistrationsEventForm(regIDs, request.POST)
        if(form.is_valid()):
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
                currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                subjects = []
                if(mode=='R' or mode=='D'):
                    subjects = BTSubjects_Staging.objects.filter(RegEventId=currentRegEventId)
                else:
                    subjects = BTSubjects.objects.filter(RegEventId=currentRegEventId)
                return render(request, 'BTco_ordinator/BTSubjectsUploadStatus.html',{'subjects':subjects,'form':form})
    else:
        form = RegistrationsEventForm(regIDs)
    return render(request, 'BTco_ordinator/BTSubjectsUploadStatus.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_delete(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    msg = ''
    if 'Cycle-Co-ordinator' in groups:
        coordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1, Dept=coordinator.Cycle, Mode='R')
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R')
    if(request.method=='POST'):
        form = SubjectDeletionForm(regIDs, request.POST)
        if('regID' in request.POST.keys()):
            if(form.is_valid()):
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
                regulation = int(strs[5])
                mode = strs[6]
                currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                if(mode=='R'): # deleting is only valid for regular registrations, the other case is not even possible
                    subjects = []
                    deletedSubjects = []
                    for sub in form.myFields:
                        if(form.cleaned_data['Check'+sub[0]]==True):
                            subject = BTSubjects_Staging.objects.filter(SubCode=sub[0],RegEventId=currentRegEventId)
                            subject.delete()
                            deletedSubjects.append(sub[0]+':' + str(sub[4]))
                        else:
                            subjects.append(sub[0])
                    if(len(deletedSubjects)!=0):
                        msg = 'Subject(s) Deleted successfully.'
                        form = SubjectDeletionForm(regIDs, request.POST)
                        return render(request,'BTco_ordinator/BTSubjectsDelete.html',{'form':form,'msg': msg})
    else:
        form = SubjectDeletionForm(regIDs)
    return render(request, 'BTco_ordinator/BTSubjectsDelete.html',{'form':form})




@login_required(login_url="/login/")
@user_passes_test(subject_access)
def subject_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    msg = ''
    if 'Cycle-Co-ordinator' in groups:
        coordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1, Dept=coordinator.Cycle, Mode='R')
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R')
    if(request.method=='POST'):
        form = SubjectFinalizeEventForm(regIDs, request.POST)
        if(form.is_valid()):
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
                currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                currentRegEventId = currentRegEventId[0].id
                subjects = []
                subjects = BTSubjects_Staging.objects.filter(RegEventId=currentRegEventId)
                for sub in subjects:
                   s=BTSubjects(SubCode=sub.SubCode,SubName=sub.SubName,Creditable=sub.Creditable,Credits=sub.Credits,\
                           OfferedBy=sub.OfferedBy,Type=sub.Type,Category=sub.Category,RegEventId=sub.RegEventId, \
                            DistributionRatio=sub.DistributionRatio, MarkDistribution=sub.MarkDistribution)
                   s.save() 
                msg = 'Subjects finalized successfully.'
    else:
        form = SubjectFinalizeEventForm(regIDs)
    return render(request, 'BTco_ordinator/BTSubjectFinalize.html',{'form':form, 'msg':msg})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def open_subject_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = []
    msg = ''
    if 'Superintendent' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if(request.method=='POST'):
        form = SubjectsUploadForm(regIDs, request.POST,request.FILES)
        if request.POST.get('upload_file_submit'):
            (ayear,asem,byear,bsem,dept,mode,regulation) = regIDs[int(request.POST['regID'])]
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear, BYear=byear, ASem=asem, BSem=bsem, Dept=dept, Mode=mode, Regulation=regulation).first().id
            if(form.is_valid()):
                if(form.cleaned_data['regID']!='--Choose Event--'):
                    file = form.cleaned_data['file']
                    data = bytes()
                    for chunk in file.chunks():
                        data += chunk
                    dataset = XLSX().create_dataset(data)
                    newDataset= Dataset()
                    errorDataset = Dataset()#To store subjects rows which are not related to present registration event
                    errorDataset.headers = ['SubCode', 'SubName', 'BYear', 'BSem', 'Dept','OfferedYear', 'Regulation',\
                        'Creditable', 'Credits','Type','Category', 'OfferedBy']
                    newDataset.headers = ['SubCode', 'SubName', 'Creditable', 'Credits', 'Type', 'Category', 'RegEventId', 'OfferedBy', \
                        'DistributionRatio', 'MarkDistribution']
                    currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                        Dept=dept,Mode=mode,Regulation=regulation)
                    currentRegEventId = currentRegEventId[0].id
                    marks_distribution = BTMarksDistribution.objects.all()
                    for i in range(len(dataset)):
                        row = dataset[i]
                        if((row[2],row[3],row[4],row[5],row[6])==(byear,bsem,dept,ayear,regulation) and row[10]=='OEC'):
                            newRow = (row[0],row[1],row[7],row[8],row[9],row[10],currentRegEventId, row[11], '', '')
                            newDataset.append(newRow)
                        else:
                            newRow = (row[0],row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8],row[9],row[10], row[11])
                            errorDataset.append(newRow)
                    request.session['newDataset'] = list(newDataset)
                    request.session['currentRegEventId'] = currentRegEventId              
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'errorRows':errorDataset, \
                    'validRows':newDataset, 'marks_distribution':marks_distribution})
        elif request.POST.get('mark_dis_submit'):
            newDataset = Dataset()
            newDataset.headers = ['SubCode', 'SubName', 'Creditable', 'Credits', 'Type', 'Category', 'RegEventId', 'OfferedBy', \
                    'DistributionRatio', 'MarkDistribution']
            errorRows = []
            for row in request.session.get('newDataset'):
                row[8] = request.POST.get('ratio_distribution_'+str(row[0])).strip()
                row[9] = int(request.POST.get('mark_distribution_'+str(row[0])))
                newRow = (row[0],row[1],row[2],row[3],row[4],row[5],row[6], row[7], row[8], row[9])
                mark_distribution = BTMarksDistribution.objects.filter(id=row[9]).first()
                if len(mark_distribution.Distribution.split(',')) != len(row[8].split(':')):
                    errorRows.append(newRow)
                else:
                    newDataset.append(newRow)
            Subject_resource = SubjectStagingResource()
            result = Subject_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                Subject_resource.import_data(newDataset, dry_run=False)
            else:
                errors = result.row_errors()
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
                    newRow = (newDataset[i][0],newDataset[i][1],newDataset[i][2],\
                        newDataset[i][3],newDataset[i][4],newDataset[i][5],newDataset[i][6], newDataset[i][7], newDataset[i][8], newDataset[i][9])
                    errorData.append(newRow)
                subErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3],\
                errorData[i][4],errorData[i][5],errorData[i][6],errorData[i][7], errorData[i][8], errorData[i][9]) for i in range(len(errorData))]
                request.session['subErrRows'] = subErrRows
                request.session['errorRows'] = errorRows
                # request.session['currentRegEventId'] = currentRegEventId              
                return HttpResponseRedirect(reverse('BTSupBTSubjectsUploadErrorHandler'))
            if errorRows:
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'errorRows1':errorRows})
            msg = 'Subjects Uploaded successfully.'

    else:
        form = SubjectsUploadForm(Options=regIDs)
    return (render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'msg':msg}))


@login_required(login_url="/login/")
@user_passes_test(subject_access)
def download_sample_subject_sheet(request):
    from BTco_ordinator.utils import SubjectsTemplateBookGenerator
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
    response['Content-Disposition'] = 'attachment; filename=sample-{model}.xlsx'.format(model='BTSubjects')
    BookGenerator = SubjectsTemplateBookGenerator()
    workbook = BookGenerator.generate_workbook()
    workbook.save(response)
    return response


def add_subjects(file):
    import pandas as pd
    file = pd.read_excel(file)
    for rIndex, row in file.iterrows():
        print(row)
        regEvent = BTRegistrationStatus.objects.filter(AYear=row[5], ASem=row[3], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[6], Mode='R').first()
        mark_dis_obj = BTMarksDistribution.objects.filter(Distribution=row[12], PromoteThreshold=row[13]).first()
        if not mark_dis_obj:
            mark_dis_obj = BTMarksDistribution(Distribution=row[12], PromoteThreshold=row[13], DistributionNames='M1+MD+M2+E')
            mark_dis_obj.save()
            mark_dis_obj = BTMarksDistribution.objects.filter(Distribution=row[12], PromoteThreshold=row[13]).first()
        if not BTSubjects_Staging.objects.filter(SubCode=row[0], RegEventId_id=regEvent.id).exists():
            subject_row = BTSubjects_Staging(SubCode=row[0], SubName=row[1], Creditable=row[7], Credits=row[8], Type=row[9], Category=row[10], OfferedBy=row[11],\
                RegEventId_id=regEvent.id, MarkDistribution=mark_dis_obj.id, DistributionRatio=row[14])
            subject_row.save()
        else:
            BTSubjects_Staging.objects.filter(SubCode=row[0], RegEventId_id=regEvent.id).update(SubName=row[1], Creditable=row[7], Credits=row[8], Type=row[9], Category=row[10], OfferedBy=row[11],\
                MarkDistribution=mark_dis_obj.id, DistributionRatio=row[14])
        
        if not BTSubjects.objects.filter(SubCode=row[0], RegEventId_id=regEvent.id).exists():
            subject_row = BTSubjects(SubCode=row[0], SubName=row[1], Creditable=row[7], Credits=row[8], Type=row[9], Category=row[10], OfferedBy=row[11],\
                RegEventId_id=regEvent.id, MarkDistribution=mark_dis_obj.id, DistributionRatio=row[14])
            subject_row.save()
        else:
            BTSubjects.objects.filter(SubCode=row[0], RegEventId_id=regEvent.id).update(SubName=row[1], Creditable=row[7], Credits=row[8], Type=row[9], Category=row[10], OfferedBy=row[11],\
                MarkDistribution=mark_dis_obj.id, DistributionRatio=row[14])
    return "Completed!!"            
