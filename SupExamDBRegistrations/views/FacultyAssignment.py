from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from SupExamDBRegistrations.forms import FacultyAssignmentForm,FacultyDeletionForm,FacultyInfoUpdateForm,BacklogRegistrationForm, RegistrationsEventForm,FacultyUploadForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, FacultyAssignmentStatusForm
from SupExamDBRegistrations.models import FacultyInfo, RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, Subjects, Subjects_Staging,\
    RollLists
from SupExamDBRegistrations.resources import FacultyInfoResource
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX



@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_upload(request):
    if(request.method=='POST'):
        form = FacultyUploadForm( request.POST,request.FILES)
        if(form.is_valid()):
                file = form.cleaned_data['file']
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                newDataset= Dataset()
                errorDataset = Dataset()#To store subjects rows which are not related to present registration event
                errorDataset.headers = ['FacultyId','Name','Phone','Email']
                newDataset.headers = ['FacultyId','Name','Phone','Email']
                fac_id =  FacultyInfo.objects.all()
                fac_id = [row.FacultyId for row in fac_id]
                for i in range(len(dataset)):
                    row = dataset[i]
                    if(row[0] not in fac_id):
                        newRow = (row[0],row[1],row[2],row[3])
                        newDataset.append(newRow)
                    else:
                        newRow = (row[0],row[1],row[2],row[3])
                        errorDataset.append(newRow)
                Faculty_resource = FacultyInfoResource()
                result = Faculty_resource.import_data(newDataset, dry_run=True)
                if not result.has_errors():
                    Faculty_resource.import_data(newDataset, dry_run=False)
                    errorData = Dataset()
                    print('errordata: ',errorData)
                    if(len(errorDataset) != 0):
                        for i in errorDataset:
                            errorData.append(i)
                        FacInfoErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3] ) for i in range(len(errorData))]
                        request.session['FacInfoErrRows'] = FacInfoErrRows
                        return HttpResponseRedirect(reverse('FacultyInfoUploadErrorHandler'))
                    # return(render(request,'SupExamDBRegistrations/FacultyInfoUploadSuccess.html'))
                else:
                    errors = result.row_errors()
                    # print(errors)
                    indices = set([i for i in range(len(newDataset))])    
                    errorIndices = set([i[0]-1 for i in errors])
                    cleanIndices = indices.difference(errorIndices)
                    cleanDataset = Dataset()
                    for i in list(cleanIndices):
                        cleanDataset.append(newDataset[i])
                    cleanDataset.headers = newDataset.headers
                
                    result1 = Faculty_resource.import_data(cleanDataset, dry_run=True)
                    if not result1.has_errors():
                        Faculty_resource.import_data(cleanDataset, dry_run=False)
                    else:
                        print('Something went wrong in plain import')
                    errorData = Dataset()
                    for i in list(errorIndices):
                        newRow1 = (newDataset[i][0],newDataset[i][1],newDataset[i][2],\
                            newDataset[i][3])
                        errorData.append(newRow1)
                    print('errordata: ',errorData)
                    for i in errorDataset:
                        errorData.append(i)
                    FacInfoErrRows = [ (errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3] ) for i in range(len(errorData))]
                    request.session['FacInfoErrRows'] = FacInfoErrRows
                    return HttpResponseRedirect(reverse('FacultyInfoUploadErrorHandler'))
                return(render(request,'SupExamDBRegistrations/FacultyInfoUploadSuccess.html'))
        else:
            print(form.errors)
            for row in form.fields.values(): print(row)
    else:
        form = FacultyUploadForm()
    return (render(request, 'SupExamDBRegistrations/FacultyUpload.html', {'form':form}))

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def FacultyInfo_upload_error_handler(request):
    FacultyInfoRows = request.session.get('FacInfoErrRows')
    for row in FacultyInfoRows:
        print(row[0])
    if(request.method=='POST'):
        form = FacultyInfoUpdateForm(FacultyInfoRows,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(FacultyInfoRows):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    FacultyInfo.objects.filter(FacultyId=fRow[0]).update(\
                        Name=fRow[1],Phone=fRow[2],Email=fRow[3])
            return render(request, 'SupExamDBRegistrations/FacultyInfoUploadSuccess.html')
    else:
        form = FacultyInfoUpdateForm(Options=FacultyInfoRows)
    return(render(request, 'SupExamDBRegistrations/FacultyInfoUploadErrorHandler.html',{'form':form}))

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def FacultyInfo_upload_status(request):
        fac_info = FacultyInfo.objects.all()
        return render(request, 'SupExamDBRegistrations/FacultyInfoStatus.html',{'fac_info': fac_info})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def Faculty_delete(request):
    fac_info = FacultyInfo.objects.all()
    fac_info = [(row.FacultyId,row.Name,row.Phone,row.Email) for row in fac_info]
    if(request.method=='POST'):
        form = FacultyDeletionForm(fac_info,request.POST)
        if(form.is_valid()):
            for cIndex, fRow in enumerate(fac_info):
                if(form.cleaned_data.get('Check'+str(fRow[0]))):
                    fac =FacultyInfo.objects.filter(FacultyId=fRow[0])
                    fac.delete()
            return render(request, 'SupExamDBRegistrations/FacultyInfoDeletionSuccess.html')
                
    else:
        form = FacultyDeletionForm(Options=fac_info)
    return render(request, 'SupExamDBRegistrations/FacultyInfoDeletion.html',{'form':form})



@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_assignment(request):
    if(request.method =='POST'):
        form = FacultyAssignmentForm(request.POST)
        print("here")
        if(form.is_valid()):
            print("here")
            regeventid=form.cleaned_data['regID']
            subjects = Subjects.objects.filter(RegEventId_id=regeventid)
            print(subjects)
            request.session['currentRegEventId']=regeventid
            return render(request, 'SupExamDBRegistrations/FacultyAssignment.html', {'form': form, 'subjects':subjects})
    
    form = FacultyAssignmentForm()
    return render(request, 'SupExamDBRegistrations/FacultyAssignment.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_assignment_status(request):
    if(request.method =='POST'):
        form = FacultyAssignmentStatusForm(request.POST)
        if(form.is_valid()):
            regeventid=form.cleaned_data['regID']
            faculty = FacultyAssignment.objects.filter(subject__RegEventId__id=regeventid)
            return render(request, 'SupExamDBRegistrations/FacultyAssignmentStatus.html',{'form':form, 'faculty':faculty})
    else:
        form = FacultyAssignmentStatusForm()
    return render(request, 'SupExamDBRegistrations/FacultyAssignmentStatus.html',{'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_assignment_detail(request,pk):
    subject = Subjects.objects.get(id=pk)
    faculty = FacultyInfo.objects.all()
    sections = RollLists.objects.filter(RegEventId_id=request.session.get('currentRegEventId')).values_list('Section', flat=True).distinct()
    faculty_assigned = FacultyAssignment.objects.filter(subject=subject)
    co_ordinator=''
    faculty_section={}
    if faculty_assigned:
        co_ordinator = faculty_assigned[0].co_ordinator_id
        faculty_section = {row.Section: row.faculty_id for row in faculty_assigned}
        print(faculty_section)
    if request.method == 'POST':
        for sec in sections:
            if request.POST.get('faculty-'+str(sec)):
                if faculty_assigned and faculty_assigned.get(Section=sec):
                    faculty_row = faculty_assigned.get(Section=sec)
                    faculty_row.co_ordinator_id = request.POST.get('course-coordinator') or 0
                    faculty_row.faculty_id = request.POST.get('faculty-'+str(sec))
                    faculty_row.save()
                else:
                    faculty_row = FacultyAssignment(subject=subject, co_ordinator_id=request.POST.get('course-coordinator'),\
                        faculty_id=request.POST.get('faculty-'+str(sec)), Section=sec)
                    faculty_row.save()
        return redirect('FacultyAssignment')
    return render(request, 'SupExamDBRegistrations/FacultyAssignmentdetail.html', {'subject':subject, 'faculty':faculty,\
        'section':sections, 'co_ordinator':co_ordinator, 'faculty_section':faculty_section})

