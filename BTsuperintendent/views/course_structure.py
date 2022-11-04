from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import redirect, render
from BTsuperintendent.models import BTCourseStructure
from BTsuperintendent.user_access_test import is_Superintendent
from BTsuperintendent.forms import CourseStructureForm, CourseStructureDeletionForm
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from BTco_ordinator.resources import CourseStructureResource

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def add_course_structre(request):
    msg = ''
    invalid_data_msg = ''
    error_data_msg = ''
    if request.method == 'POST':
        form = CourseStructureForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data.get('file')
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset=  XLSX().create_dataset(data)
            newDataset = Dataset()
            invalidDataset = []
            errorData = []
            newDataset.headers = ['BYear', 'BSem', 'Dept', 'Regulation', 'Category', 'Type', 'Creditable', 'Credits']
            for row in dataset:
                if row[3] == form.cleaned_data.get('regulation'):
                    newRow = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    newDataset.append(newRow)
                else:
                    newRow = (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
                    invalidDataset.append(newRow)
            course_str_resource = CourseStructureResource()
            result = course_str_resource.import_data(newDataset, dry_run=True)
            if not result.has_erros():
                course_str_resource.import_data(newDataset, dry_run=False)
            else:
                errors = result.row_errors()
                indices = set([i for i in range(len(newDataset))])    
                errorIndices = set([i[0]-1 for i in errors])
                cleanIndices = indices.difference(errorIndices)
                cleanDataset = Dataset()
                for i in list(cleanIndices):
                    cleanDataset.append(newDataset[i])
                cleanDataset.headers = newDataset.headers

                next_result = course_str_resource.import_data(cleanDataset, dry_run=True)
                if not next_result.has_errors():
                    course_str_resource.import_data(cleanDataset, dry_run=False)
                for i in list(errorIndices):
                    newRow = (newDataset[i][0],newDataset[i][1],newDataset[i][2],\
                        newDataset[i][3],newDataset[i][4],newDataset[i][5],newDataset[i][6], newDataset[i][7])
                    errorData.append(newRow)
            if invalidDataset:
                invalid_data_msg = 'This data has regulation different from the selected regulation.'
            if errorData:
                error_data_msg = 'This data has some errors.'
            if not invalidDataset and not errorData:
                msg = 'Course Structure Uploaded successfully.'
            return render(request, 'BTsuperintendent/CourseStructure.htm', {'form':form, 'invalidRows':invalidDataset, 'errorData':errorData, 'msg':msg, 'invalid_data_msg':invalid_data_msg, 'error_data_msg':error_data_msg})
    else:
        form = CourseStructureForm()
    return render(request, 'BTsuperintendent/CourseStructure.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def course_structure_delete(request):
    if(request.method=='POST'):
        form = CourseStructureDeletionForm(request.POST)
        if 'submit-form' in request.POST.keys():
            if form.is_valid():
                deleted_cs = []
                for cs in form.myFields:
                    if form.cleaned_data.get('Check'+cs.id) == True:
                        course_str = BTCourseStructure.objects.get(id=cs.id)
                        course_str.delete()
                        deleted_cs.append(course_str)  
                if deleted_cs:
                    msg = 'CourseStructure deleted successfully.'
                    form = CourseStructureDeletionForm(request.POST)
                    return render(request, 'BTsuperintendent/BTCourseStructureDelete.html',{'form':form, 'msg':msg})
    else:
        form = CourseStructureDeletionForm()
    return render(request, 'BTsuperintendent/BTCourseStructureDelete.html',{'form':form})

