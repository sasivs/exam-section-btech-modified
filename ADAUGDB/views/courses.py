from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse 
from django.shortcuts import render
from ADAUGDB.models import BTCourseStructure, BTCourses, BTMarksDistribution
from ADAUGDB.resources import BTCoursesResource
from ADAUGDB.user_access_test import is_Associate_Dean_Academics, course_status_access
from ADAUGDB.forms import AddCoursesForm, CoursesStatusForm
from import_export.formats.base_formats import XLSX
from tablib import Dataset
import copy

@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def add_courses(request):
    msg = ''
    if request.method == 'POST':
        form = AddCoursesForm(request.POST, request.FILES)
        if form.is_valid():
            if request.POST.get('Submit'):
                file = form.cleaned_data.get('file')
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                newDataset= Dataset()
                invalidData = []
                newDataset.headers = ['SubCode', 'SubName', 'OfferedBy', 'CourseStructure', 'lectures', 'tutorials', 'practicals',\
                            'DistributionRatio', 'MarkDistribution']
                data_rows = [] 
                for row in dataset:
                    if (row[2], row[6]) != (form.cleaned_data.get('BYear'), form.cleaned_data.get('Regulation')):
                        invalidData.append(row)
                        continue
                    course_struct_obj = BTCourseStructure.objects.filter(Category=row[10], Type=row[9], Creditable=row[7], Credits=row[8],\
                        Regulation=row[6], BYear=row[2], BSem=row[3], Dept=row[4]).first()
                    mark_dis = row[15].split(';')
                    mark_distribution = BTMarksDistribution.objects.filter(Regulation=form.cleaned_data.get('Regulation'), Distribution=mark_dis[0], \
                        DistributionNames=mark_dis[-1], PromoteThreshold=mark_dis[1]).first()
                    newRow = (row[0], row[1], row[5], course_struct_obj.id, row[11], row[12], row[13], row[14], mark_distribution.id)

                    newDataset.append(newRow)
                courses_resource = BTCoursesResource()
                result = courses_resource.import_data(newDataset, dry_run=True)
                
                if not result.has_errors():
                    courses_resource.import_data(newDataset, dry_run=False)
                    msg = 'Courses Uploaded successfully'
                    return render(request, 'ADAUGDB/AddCourses.html', {'form':form, 'invalidData':invalidData, 'msg': msg})
                else:
                    errors = result.row_errors()
                    print(errors[0][1][0].__dict__)
                    # print(errors.error())
                    indices = set([i for i in range(len(newDataset))])    
                    errorIndices = set([i[0]-1 for i in errors])
                    cleanIndices = indices.difference(errorIndices)
                    cleanDataset = Dataset()
                    for i in list(cleanIndices):
                        cleanDataset.append(newDataset[i])
                    cleanDataset.headers = newDataset.headers

                    result1 = courses_resource.import_data(cleanDataset, dry_run=True)
                    if not result1.has_errors():
                        courses_resource.import_data(cleanDataset, dry_run=False)

                    errorRows = []
                    for i in errorIndices:
                        errorRows.append(dataset[i])
                    if errorRows:
                        return render(request, 'ADAUGDB/AddCourses.html', {'form':form, 'errorRows': errorRows, 'invalidData':invalidData})
                    msg = 'Courses Uploaded successfully'
                    return render(request, 'ADAUGDB/AddCourses.html', {'form':form, 'invalidData':invalidData, 'msg': msg})
            elif request.POST.get('download'):
                from ADAUGDB.utils import CoursesTemplateExcelFile
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                response['Content-Disposition'] = 'attachment; filename=R-{regulation}_BYear-{byear}.xlsx'.format(regulation=form.cleaned_data.get('Regulation'), byear=form.cleaned_data.get("BYear"))
                BookGenerator = CoursesTemplateExcelFile(form.cleaned_data.get('Regulation'), form.cleaned_data.get('BYear'))
                workbook = BookGenerator.generate_workbook()
                workbook.save(response)
                return response
    else:
        form = AddCoursesForm() 
    return render(request, 'ADAUGDB/AddCourses.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(course_status_access)
def course_upload_status(request):
    if(request.method=='POST'):
        form = CoursesStatusForm(request.POST)
        if(form.is_valid()):
            courses = BTCourses.objects.filter(CourseStructure__Regulation=form.cleaned_data.get('Regulation'), CourseStructure__BYear=form.cleaned_data.get('BYear'))
            return render(request, 'ADAUGDB/CoursesStatus.html', {'form':form, 'courses':courses})
    else:
        form = CoursesStatusForm()
    return render(request, 'ADAUGDB/CoursesStatus.html',{'form':form})
