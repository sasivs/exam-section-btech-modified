from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import is_Associate_Dean_Academics, curriculum_components_status_access
from django.shortcuts import render
from django.db import transaction
from django.http import HttpResponse
from ADAUGDB.forms import CurriculumComponentsUploadForm, CurriculumComponentsStatusForm, CurriculumComponentsDeleteForm
from ADAUGDB.models import BTCurriculumComponents
from import_export.formats.base_formats import XLSX
from tablib import Dataset
from ADAUGDB.resources import CurriculumComponentsResource

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def curriculum_components_upload(request):
    msg = ''
    invalid_data_msg = ''
    error_data_msg = ''
    if request.method == 'POST':
        if request.POST.get('Submit'):
            form = CurriculumComponentsUploadForm(request.POST, request.FILES)
            if form.is_valid():
                file = form.cleaned_data.get('file')
                data = bytes()
                for chunk in file.chunks():
                    data+=chunk
                dataset = XLSX().create_dataset(data)
                newDataset = Dataset()
                invalidDataset = []
                errorData = []
                newDataset.headers = ['Regulation', 'Dept', 'Category', 'CreditsOffered', 'MinimumCredits']
                for row in dataset:
                    if (float(row[0]), row[1]) == (form.cleaned_data.get('Regulation'), int(form.cleaned_data.get('Dept'))):
                        newRow = (row[0], row[1], row[2], row[3], row[4])
                        newDataset.append(newRow)
                    else:
                        newRow = (row[0], row[1], row[2], row[3], row[4])
                        invalidDataset.append(newRow)
                
                curriculum_components_resource = CurriculumComponentsResource()
                result = curriculum_components_resource.import_data(newDataset, dry_run=True)

                if not result.has_errors():
                    curriculum_components_resource.import_data(newDataset, dry_run=False)
                else:
                    errors = result.row_errors()
                    for er in errors:
                        print(er[1][0].__dict__['error'])
                        print(er[1][0].__dict__['row'])

                    indices = set([i for i in range(len(newDataset))])    
                    errorIndices = set([i[0]-1 for i in errors])
                    cleanIndices = indices.difference(errorIndices)
                    cleanDataset = Dataset()
                    for i in list(cleanIndices):
                        cleanDataset.append(newDataset[i])
                    cleanDataset.headers = newDataset.headers
                    next_result = curriculum_components_resource.import_data(cleanDataset, dry_run=True)
                    if not next_result.has_errors():
                        curriculum_components_resource.import_data(cleanDataset, dry_run=False)
                    for i in list(errorIndices):
                        errorData.append(newDataset[i])
                    
                if invalidDataset:
                    invalid_data_msg = 'This data has regulation and department different from the selected regulation and department.'
                if errorData:
                    error_data_msg = 'This data has some errors.'
                if not invalidDataset and not errorData:
                    msg = 'Curriculum components Uploaded successfully.'
                return render(request, 'ADAUGDB/BTCurriculumComponentsUpload.html', {'form':form, 'invalidRows':invalidDataset, 'errorData':errorData, 'msg':msg, 'invalid_data_msg':invalid_data_msg, 'error_data_msg':error_data_msg})
        elif request.POST.get('download'):
            from BTco_ordinator.utils import ModelTemplateBookGenerator
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
            response['Content-Disposition'] = 'attachment; filename=sample-{model}.xlsx'.format(model='CurriculumComponents_model')
            BookGenerator = ModelTemplateBookGenerator(BTCurriculumComponents)
            workbook = BookGenerator.generate_workbook()
            workbook.save(response)
            return response
    else:
        form = CurriculumComponentsUploadForm()
    return render(request, 'ADAUGDB/BTCurriculumComponentsUpload.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(curriculum_components_status_access)
def curriculum_components_status(request):
    if(request.method=='POST'):
        form = CurriculumComponentsStatusForm(request.POST)
        if form.is_valid():
            curriculum_components = BTCurriculumComponents.objects.filter(Dept=form.cleaned_data.get('Dept'), Regulation=form.cleaned_data.get('Regulation'))
            return render(request, 'ADAUGDB/BTCurriculumComponentsStatus.html',{'form':form, 'curriculum_components':curriculum_components})
    else:
        form = CurriculumComponentsStatusForm()
    return render(request, 'ADAUGDB/BTCurriculumComponentsStatus.html',{'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def curriculum_components_delete(request):
    if(request.method=='POST'):
        form = CurriculumComponentsDeleteForm(request.POST)
        if 'delete-form' in request.POST.keys():
            if form.is_valid():
                curriculum_components = BTCurriculumComponents.objects.filter(Dept=form.cleaned_data.get('Dept'), Regulation=form.cleaned_data.get('Regulation'))
                deleted_cc = []
                for cc in curriculum_components:
                    if request.POST.get('Check'+str(cc.id)) == 'delete':
                        cc.delete()
                        deleted_cc.append(cc)  
                if deleted_cc:
                    msg = 'CourseStructure deleted successfully.'
                    curriculum_components = BTCurriculumComponents.objects.filter(Dept=form.cleaned_data.get('Dept'), Regulation=form.cleaned_data.get('Regulation'))
                    return render(request, 'ADAUGDB/BTCurriculumComponentsDelete.html',{'form':form, 'msg':msg, 'curriculum_components':curriculum_components})
        elif 'submit-form' in request.POST.keys():
            curriculum_components = BTCurriculumComponents.objects.filter(Dept=int(request.POST.get('Dept')), Regulation=float(request.POST.get('Regulation')))
        return render(request, 'ADAUGDB/BTCurriculumComponentsDelete.html', {'form':form, 'curriculum_components':curriculum_components})
    else:
        form = CurriculumComponentsDeleteForm()
    return render(request, 'ADAUGDB/BTCurriculumComponentsDelete.html',{'form':form})
