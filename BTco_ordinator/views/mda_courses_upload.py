from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponse 
from ADAUGDB.resources import BTCoursesResource
from ADAUGDB.models import BTCycleCoordinator, BTRegistrationStatus, BTCourseStructure, BTMarksDistribution,BTCourses
from BThod.models import BTCoordinator
from BTco_ordinator.models import BTSubjects_Staging, BTSubjects
from BTco_ordinator.forms import MDACoursesUploadForm, SubjectFinalizeEventForm
from ADAUGDB.user_access_test import mda_subject_access
from import_export.formats.base_formats import XLSX
from tablib import Dataset
from django.db import transaction

@login_required(login_url="/login/")
@user_passes_test(mda_subject_access)
def add_mda_courses(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = []
    if 'Cycle-Co-ordinator' in groups:
        coordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_course_structures = BTCourseStructure.objects.filter(Category__in=['MDA'], BYear=1, Dept=coordinator.Cycle) 
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1, Dept=coordinator.Cycle, Mode='R').\
            filter(Dept__in=valid_course_structures.values_list('Dept', flat=True), BSem__in=valid_course_structures.values_list('BSem', flat=True))
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_course_structures = BTCourseStructure.objects.filter(Category__in=['MDA'], BYear=coordinator.BYear, Dept=coordinator.Dept) 
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R', \
            BSem__in=valid_course_structures.values_list('BSem', flat=True))
    if request.method == 'POST':
        form = MDACoursesUploadForm(regIDs, request.POST)
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
                event = regIDs.filter(id=form.cleaned_data.get('regID')).first()
                for row in dataset:
                    if (row[2], row[3], row[4], row[6]) != (event.BYear, event.BSem, event.Dept, event.Regulation):
                        invalidData.append(row)
                        continue
                    course_struct_obj = BTCourseStructure.objects.filter(Category=row[10].upper(), Type=row[9].upper(), Creditable=row[7], Credits=row[8],\
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
                        with transaction.atomic():
                            course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Category__in=['MDA'])
                            courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
                            for course in courses:
                                if not BTSubjects_Staging.objects.filter(RegEventId_id=event.id, course_id=course.id).exists():
                                    subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                                    subject_row.save()
                        msg = 'Courses Uploaded successfully'
                        return render(request, 'BTco_ordinator/MDAcoursesUpload.html', {'form':form, 'invalidData':invalidData, 'msg': msg})
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
                            with transaction.atomic():
                                course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Category__in=['MDA'])
                                courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
                                for course in courses:
                                    if not BTSubjects_Staging.objects.filter(RegEventId_id=event.id, course_id=course.id).exists():
                                        subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                                        subject_row.save()
                        errorRows = []
                        for i in errorIndices:
                            errorRows.append(dataset[i])
                        if errorRows:
                            return render(request, 'BTco_ordinator/MDAcoursesUpload.html', {'form':form, 'errorRows': errorRows, 'invalidData':invalidData})
                        msg = 'Courses Uploaded successfully'
                        return render(request, 'BTco_ordinator/MDAcoursesUpload.htmll', {'form':form, 'invalidData':invalidData, 'msg': msg})
            elif request.POST.get('download'):
                from ADAUGDB.utils import CoursesTemplateExcelFile
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                response['Content-Disposition'] = 'attachment; filename=R-{regulation}_BYear-{byear}.xlsx'.format(regulation=form.cleaned_data.get('Regulation'), byear=form.cleaned_data.get("BYear"))
                BookGenerator = CoursesTemplateExcelFile(event.Regulation, event.BYear)
                workbook = BookGenerator.generate_workbook()
                workbook.save(response)
                return response
        pass
    else:
        form = MDACoursesUploadForm(regIDs)
    return render('BTco_ordinator/MDAcoursesUpload.html', {'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(mda_subject_access)
def mda_subject_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    msg = ''
    if 'Cycle-Co-ordinator' in groups:
        coordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_course_structures = BTCourseStructure.objects.filter(Category__in=['MDA'], BYear=1, Dept=coordinator.Cycle) 
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1, Dept=coordinator.Cycle, Mode='R').\
            filter(Dept__in=valid_course_structures.values_list('Dept', flat=True), BSem__in=valid_course_structures.values_list('BSem', flat=True))
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        valid_course_structures = BTCourseStructure.objects.filter(Category__in=['MDA'], BYear=coordinator.BYear, Dept=coordinator.Dept) 
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R', \
            BSem__in=valid_course_structures.values_list('BSem', flat=True))
    if(request.method=='POST'):
        form = SubjectFinalizeEventForm(regIDs, request.POST)
        if(form.is_valid()):
            subjects = []
            subjects = BTSubjects_Staging.objects.filter(RegEventId_id=form.cleaned_data.get('regID'), course__CourseStructure__in=['MDA'])
            for sub in subjects:
                s=BTSubjects(RegEventId_id=sub.RegEventId_id, course_id=sub.course_id)
                s.save() 
            msg = 'Subjects finalized successfully.'
    else:
        form = SubjectFinalizeEventForm(regIDs)
    return render(request, 'BTco_ordinator/BTSubjectFinalize.html',{'form':form, 'msg':msg})
