from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
from SupExamDBRegistrations.forms import BacklogRegistrationForm, RegistrationsEventForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, DroppedRegularRegistrationsForm,\
        MakeupRegistrationsForm, NotPromotedListForm, NotPromotedUploadForm, NotPromotedUpdateForm, NotPromotedStatusForm
from SupExamDBRegistrations.models import MandatoryCredits, NotPromotedResource, RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, \
    SubjectStagingResource, Subjects, Subjects_Staging, DroppedRegularCourses, StudentRegistrations_Staging, RollLists,StudentGradePoints,\
        NotPromoted
from SupExamDBRegistrations.views import RollList
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F,Q
from tablib import Dataset
from import_export.formats.base_formats import XLSX
import pandas as pd
from AWSP.settings import MEDIA_ROOT
import mimetypes
import os
from django.http.response import HttpResponse
# Import render module
from django.shortcuts import render


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
            if byear != 1:
                rolls = RollLists.objects.filter(AYear=ayear, BYear=byear, Dept=dept, Regulation=regulation)
            else:
                rolls = RollLists.objects.filter(AYear=ayear, BYear=byear, Cycle=dept, Regulation=regulation)
            mandatory_credits = MandatoryCredits.objects.filter(Regulation=regulation, BYear=byear, Dept=dept)
            mandatory_credits = mandatory_credits[0].Credits
            np = []
            excel_data = {'RegNo':[], 'AYear':[], 'BYear':[], 'PoA':[]}
            for roll in rolls:
                regno = roll.RegNo
                grades = StudentGradePoints.objects.filter(RegNo=regno, AYear=ayear, BYear=byear).filter(~Q(Grade='F')).\
                    filter(~Q(Grade='I')).filter(~Q(Grade='X')).filter(~Q(Grade='R'))
                credits=0
                for g in grades:
                    credits += g.Credits
                if credits < mandatory_credits:
                    d = {'RegNo':regno, 'AYear':ayear, 'BYear':byear, 'PoA':'R'}
                    np.append(d)
                    excel_data['RegNo'].append(d['RegNo'])
                    excel_data['AYear'].append(d['AYear'])
                    excel_data['BYear'].append(d['BYear'])
                    excel_data['PoA'].append(d['PoA'])
                else:
                    if byear == 2 or byear == 3:
                        backlogs = StudentBacklogs.objects.filter(RegNo=regno, BYear=byear-1)
                        if len(backlogs) != 0:
                            d = {'RegNo':regno, 'AYear':ayear, 'BYear':byear, 'PoA':'B'}
                            np.append(d)
                            excel_data['RegNo'].append(d['RegNo'])
                            excel_data['AYear'].append(d['AYear'])
                            excel_data['BYear'].append(d['BYear'])
                            excel_data['PoA'].append(d['PoA'])
                        else:
                            dropped_courses = DroppedRegularCourses.objects.filter(RegNo=regno)
                            for course in dropped_courses:
                                sub = Subjects.objects.get(id=course.sub_id)
                                offeredEvent = RegistrationStatus.objects.get(id=sub.RegEventId)
                                if offeredEvent.BYear == byear-1:
                                    check_registration = StudentRegistrations.objects.filter(RegNo=regno, sub_id=course.sub_id)
                                    if len(check_registration) == 0:
                                        d = {'RegNo':regno, 'AYear':ayear, 'BYear':byear, 'PoA':'B'}
                                        np.append(d)
                                        excel_data['RegNo'].append(d['RegNo'])
                                        excel_data['AYear'].append(d['AYear'])
                                        excel_data['BYear'].append(d['BYear'])
                                        excel_data['PoA'].append(d['PoA'])
                    elif byear == 4:
                        backlogs = StudentBacklogs.objects.filter(RegNo=regno)
                        if len(backlogs) != 0:
                            d = {'RegNo':regno, 'AYear':ayear, 'BYear':byear, 'PoA':'B'}
                            np.append(d)
                            excel_data['RegNo'].append(d['RegNo'])
                            excel_data['AYear'].append(d['AYear'])
                            excel_data['BYear'].append(d['BYear'])
                            excel_data['PoA'].append(d['PoA'])
                        else:
                            dropped_courses = DroppedRegularCourses.objects.filter(RegNo=regno)
                            for course in dropped_courses:
                                sub = Subjects.objects.get(id=course.sub_id)
                                check_registration = StudentRegistrations.objects.filter(RegNo=regno, sub_id=course.sub_id)
                                if len(check_registration) == 0:
                                    d = {'RegNo':regno, 'AYear':ayear, 'BYear':byear, 'PoA':'B'}
                                    np.append(d)
                                    excel_data['RegNo'].append(d['RegNo'])
                                    excel_data['AYear'].append(d['AYear'])
                                    excel_data['BYear'].append(d['BYear'])
                                    excel_data['PoA'].append(d['PoA'])
            event = event.replace(':','_')
            dname = str(event)+".xlsx"
            name=MEDIA_ROOT + str(event) + ".xlsx"
            reqData = pd.DataFrame.from_dict(excel_data)
            writer = pd.ExcelWriter(name, engine='xlsxwriter')
            reqData.to_excel(writer, sheet_name='Sheet1', index=False)
            writer.save()
            request.session['filename']=dname
            request.session['filepath']=name
            return render(request, 'SupExamDBRegistrations/NotPromotedList.html', {'form':form, 'notPromoted':np, 'download_link':name, 'download_name':dname})
    else:
        form = NotPromotedListForm()
    return render(request, 'SupExamDBRegistrations/NotPromotedList.html', {'form':form})

# Import mimetypes module
# import os module
# Import HttpResponse module


# Define function to download pdf file using template
def download_file(request):
    filepath=request.session.get('filepath')
    filename = request.session.get('filename')
    path = open(filepath, 'rb')
    mime_type, _ = mimetypes.guess_type(filepath)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response

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
            newDataset.headers =['RegNo', 'AYear', 'BYear', 'PoA']
            errorDataset = Dataset()
            errorDataset.headers=['RegNo', 'AYear', 'BYear', 'PoA']
            for i in range(len(dataset)):
                row = dataset[i]
                if row[1] == ayear and row[2] == byear:
                    newRow = (row[0],row[1],row[2],row[3])
                    newDataset.append(newRow)
                else:
                    newRow = (row[0],row[1],row[2],row[3])
                    errorDataset.append(newRow)
            not_promoted_resource = NotPromotedResource()
            result = not_promoted_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                not_promoted_resource.import_data(newDataset, dry_run=False)
                if (len(errorDataset)!=0):
                    npErrRows = [(errorDataset[i][0],errorDataset[i][1],errorDataset[i][2],errorDataset[i][3]) for i in range(len(errorDataset))]
                    request.session['npErrRows'] = npErrRows
                    request.session['RegEvent'] = regEvent
                    return HttpResponseRedirect(reverse('NotPromotedUploadErrorHandler' ))
                return(render(request,'SupExamDBRegistrations/NotPromotedUploadSuccess.html'))
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
                
                result1 = not_promoted_resource.import_data(cleanDataset, dry_run=True)
                if not result1.has_errors():
                    not_promoted_resource.import_data(cleanDataset, dry_run=False)
                else:
                        print('Something went wrong in plain import')
                errorData = Dataset()
                for i in list(errorIndices):
                    newRow = (newDataset[i][0],newDataset[i][1],newDataset[i][2],newDataset[i][3])
                    errorData.append(newRow)
                for i in errorDataset:
                    errorData.append(i)
                npErrRows = [(errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3]) for i in range(len(errorData))]
                request.session['npErrRows'] = npErrRows
                request.session['RegEvent'] = regEvent
                return HttpResponseRedirect(reverse('NotPromotedUploadErrorHandler' ))
    else:
        form = NotPromotedUploadForm()
    return render(request, 'SupExamDBRegistrations/NotPromotedUpload.html', {'form':form})


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
                    NotPromoted.objects.filter(RegNo=fRow[0],AYear=fRow[1], BYear=fRow[2]).update(PoA=fRow[3])
            return render(request, 'SupExamDBRegistrations/NotPromotedUploadSuccess.html')
    else:
        form = NotPromotedUpdateForm(Options=npErrRows)
    return(render(request, 'SupExamDBRegistrations/NotPromotedUploadErrorHandler.html',{'form':form}))

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
            notPromoted = NotPromoted.objects.filter(AYear=ayear, BYear=byear)
            print(notPromoted)
            return render(request, 'SupExamDBRegistrations/NotPromotedStatus.html', {'notPromoted':notPromoted.values(), 'form':form})
    else:
        form = NotPromotedStatusForm()
    return render(request, 'SupExamDBRegistrations/NotPromotedStatus.html', {'form':form})
