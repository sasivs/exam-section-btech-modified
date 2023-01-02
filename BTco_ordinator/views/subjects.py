
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import HttpResponse
from django.shortcuts import render
from BTco_ordinator.forms import RegistrationsEventForm, SubjectsUploadForm, StudentRegistrationUpdateForm, \
    SubjectDeletionForm, SubjectFinalizeEventForm, SubjectsSelectForm
from BTco_ordinator.models import BTSubjects_Staging, BTSubjects
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTHOD, BTMarksDistribution, BTCycleCoordinator, BTCourses, BTCourseStructure
from BThod.models import BTCoordinator
from ADAUGDB.user_access_test import subject_access, subject_home_access, is_Associate_Dean_Academics, dept_elective_subject_upload_access
from django.db import transaction

@transaction.atomic
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
        regIDs = [(row.id, row.__str__()) for row in regIDs]
    if(request.method=='POST'):
        if request.POST.get('name') == 'SubjectsUploadForm':
            form = SubjectsUploadForm(regIDs, request.POST)
            if form.is_valid():
                event = BTRegistrationStatus.objects.get(id=form.cleaned_data.get('regID'))
                course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept).exclude(Category__in=['OEC', 'OPC'])
                courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
                excessCourses = []
                slackCourses = []
                BTSubjects_Staging.objects.filter(RegEventId_id=event.id).exclude(course__CourseStructure__Category__in=['OEC', 'OPC']).delete()
                for c_str in course_structure:
                    related_courses = courses.filter(CourseStructure_id=c_str.id)
                    if len(related_courses)==c_str.count:
                        for course in courses.filter(CourseStructure_id=c_str.id):
                            if not BTSubjects_Staging.objects.filter(RegEventId_id=event.id, course_id=course.id).exists():
                                subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                                subject_row.save()
                    elif len(related_courses) > c_str.count:
                        excessCourses.append((c_str, related_courses))
                    else:
                        slackCourses.append((c_str, related_courses))
                if excessCourses:
                    excessCoursesDict = {c_str.id:[c_str.count, c_str.Category] for c_str, _ in excessCourses}
                    form = SubjectsSelectForm(excessCourses, event)
                    from json import dumps
                    return render(request, 'BTco_ordinator/BTSubjectsUpload.html',{'form':form, 'excess':dumps(excessCoursesDict)})
                if not slackCourses:
                    msg = 'Subjects uploaded successfully.'
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'slackCourses': slackCourses, 'msg':msg} )
        elif request.POST.get('name') == 'SubjectsSelectForm':
            event = BTRegistrationStatus.objects.get(id=request.POST.get('event'))
            course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept)
            courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
            excessCourses = []
            slackCourses = []
            for c_str in course_structure:
                related_courses = courses.filter(CourseStructure_id=c_str.id)
                if len(related_courses) > c_str.count:
                        excessCourses.append((c_str, related_courses))
                elif len(related_courses) < c_str.count:
                    slackCourses.append((c_str, related_courses))
            form = SubjectsSelectForm(excessCourses, event, request.POST)
            if form.is_valid():
                for course_tup in excessCourses:
                    for course in course_tup[1]:
                        if form.cleaned_data.get('Check'+str(course.id)):
                            if not BTSubjects_Staging.objects.filter(RegEventId_id=event.id, course_id=course.id).exists():
                                subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                                subject_row.save()
                if not slackCourses:
                    msg = 'Subjects uploaded successfully.'
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'slackCourses':slackCourses, 'msg':msg})

    else:
        form = SubjectsUploadForm(Options=regIDs)
    return (render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'msg':msg}))

@transaction.atomic
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
    if 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode__in=['R','B'])
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode_in=['R','B'])
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=co_ordinator.BYear, Dept=co_ordinator.Dept, Mode_in=['R','B'])
    elif 'Cycle-Co-ordinator' in groups:
        co_ordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Cycle, Mode_in=['R','B'])
    if regIDs:
        regIDs = [(row.id, row.__str__()) for row in regIDs]
    if(request.method=='POST'):
        form = RegistrationsEventForm(regIDs, request.POST)
        if(form.is_valid()):
            currentRegEventId = BTRegistrationStatus.objects.get(id=form.cleaned_data.get('regID'))
            subjects = []
            subjects = BTSubjects_Staging.objects.filter(RegEventId=currentRegEventId)
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
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=1, Dept=coordinator.Cycle, Mode_in=['R','B'])
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode_in=['R','B'])
    if(request.method=='POST'):
        form = SubjectDeletionForm(regIDs, request.POST)
        if('regID' in request.POST.keys()):
            if(form.is_valid()):
                currentRegEventId = BTRegistrationStatus.objects.get(id=form.cleaned_data.get('regID'))
                deletedSubjects = []
                for sub in form.myFields:
                    if(form.cleaned_data['Check'+str(sub[-1])]==True):
                        subject = BTSubjects_Staging.objects.filter(id=sub[-1],RegEventId=currentRegEventId)
                        subject.delete()
                        deletedSubjects.append(sub[0]+':' + str(sub[4]))
                if(len(deletedSubjects)!=0):
                    msg = 'Subject(s) Deleted successfully.'
                    form = SubjectDeletionForm(regIDs, request.POST)
                    return render(request,'BTco_ordinator/BTSubjectsDelete.html',{'form':form,'msg': msg})
    else:
        form = SubjectDeletionForm(regIDs)
    return render(request, 'BTco_ordinator/BTSubjectsDelete.html',{'form':form})



@transaction.atomic
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
        backlog_regIDs = BTSubjects_Staging.objects.filter(RegEventId__Status=1, RegEventId__RegistrationsStatus=1, RegEventId__BYear=coordinator.BYear, RegEventId__Dept=coordinator.Dept, RegEventId__Mode='B')
        regIDs |= BTRegistrationStatus.objects.filter(id__in=backlog_regIDs.values_list('RegEventId_id', flat=True))
    elif 'Associate-Dean-Academics' in groups:
        subjects = BTSubjects_Staging.objects.filter(RegEventId__Status=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
        regIDs = BTRegistrationStatus.objects.filter(id__in=subjects.values_list('RegEventId_id', flat=True))
    if(request.method=='POST'):
        form = SubjectFinalizeEventForm(regIDs, request.POST)
        if(form.is_valid()):
            subjects = []
            if 'Associate-Dean-Academics' in groups:
                subjects = BTSubjects_Staging.objects.filter(RegEventId_id=form.cleaned_data.get('regID'), \
                    course__CourseStructure__Category__in=['OEC', 'OPC'])
            else:
                subjects = BTSubjects_Staging.objects.filter(RegEventId_id=form.cleaned_data.get('regID'))
            for sub in subjects:
                s=BTSubjects(RegEventId_id=sub.RegEventId_id, course_id=sub.course_id)
                s.save() 
            msg = 'Subjects finalized successfully.'
    else:
        form = SubjectFinalizeEventForm(regIDs)
    return render(request, 'BTco_ordinator/BTSubjectFinalize.html',{'form':form, 'msg':msg})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def open_subject_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = []
    msg = ''
    if 'Associate-Dean-Academics' in groups:
        course_structure_obj = BTCourseStructure.objects.filter(Category__in=['OEC', 'OPC'])
        regIDs = BTRegistrationStatus.objects.none()
        for course_struc in course_structure_obj:
            regIDs |= BTRegistrationStatus.objects.filter(Status=1, OERegistrationStatus=1, Mode__in=['R','B'], Regulation=course_struc.Regulation, \
                BYear=course_struc.BYear, BSem=course_struc.BSem,Dept=course_struc.Dept)
    if regIDs:
        regIDs = [(row.id, row.__str__()) for row in regIDs]
    if(request.method=='POST'):
        if request.POST.get('name') == 'SubjectsUploadForm':
            form = SubjectsUploadForm(regIDs, request.POST)
            if form.is_valid():
                event = BTRegistrationStatus.objects.get(id=form.cleaned_data.get('regID'))
                course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Category__in=['OEC', 'OPC'])
                courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
                excessCourses = []
                slackCourses = []
                BTSubjects_Staging.objects.filter(RegEventId_id=event.id, course__CourseStructure__Category__in=['OEC', 'OPC']).delete()
                for c_str in course_structure:
                    related_courses = courses.filter(CourseStructure_id=c_str.id)
                    if not related_courses or len(related_courses) < c_str.count:
                        slackCourses.append((c_str, related_courses))
                    elif len(related_courses) > c_str.count:
                        excessCourses.append((c_str, related_courses))
                    elif len(related_courses) == c_str.count:
                        for course in related_courses:
                            subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                            subject_row.save()
                if excessCourses:
                    excessCoursesDict = {c_str.id:[c_str.count, c_str.Category] for c_str, _ in excessCourses}
                    form = SubjectsSelectForm(excessCourses, event)
                    from json import dumps
                    return render(request, 'BTco_ordinator/BTSubjectsUpload.html',{'form':form, 'excess':dumps(excessCoursesDict)})
                msg=''
                if not slackCourses:
                    msg = 'Subjects uploaded successfully.'
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'slackCourses': slackCourses, 'msg':msg})
        elif request.POST.get('name') == 'SubjectsSelectForm':
            event = BTRegistrationStatus.objects.get(id=request.POST.get('event'))
            course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept)
            courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
            excessCourses = []
            slackCourses = []
            for c_str in course_structure:
                related_courses = courses.filter(CourseStructure_id=c_str.id)
                if len(related_courses) > c_str.count:
                        excessCourses.append((c_str, related_courses))
                elif len(related_courses) < c_str.count:
                    slackCourses.append((c_str, related_courses))
            form = SubjectsSelectForm(excessCourses, event, request.POST)
            if form.is_valid():
                for course_tup in excessCourses:
                    for course in course_tup[1]:
                        if form.cleaned_data.get('Check'+str(course.id)):
                            subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                            subject_row.save()
                msg = ''
                if not slackCourses:
                    msg = 'Subjects uploaded successfully.'
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'slackCourses':slackCourses, 'msg':msg})
    else:
        form = SubjectsUploadForm(Options=regIDs)
    return (render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'msg':msg}))

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(dept_elective_subject_upload_access)
def dept_elective_subject_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = []
    msg = ''
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        course_structures = BTCourseStructure.objects.filter(BYear=coordinator.BYear, Dept=coordinator.Dept, Category='DEC')
        if course_structures:
            regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, BYear=coordinator.BYear, Dept=coordinator.Dept, BSem__in=course_structures.distinct('BSem').values_list('BSem', flat=True), Mode='B')
    if regIDs:
        regIDs = [(row.id, row.__str__()) for row in regIDs]
    else:
        regIDs = []
    if(request.method=='POST'):
        if request.POST.get('name') == 'SubjectsUploadForm':
            form = SubjectsUploadForm(regIDs, request.POST)
            if form.is_valid():
                event = BTRegistrationStatus.objects.get(id=form.cleaned_data.get('regID'))
                course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Category__in=['OEC', 'OPC'])
                courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
                excessCourses = []
                slackCourses = []
                BTSubjects_Staging.objects.filter(RegEventId_id=event.id, course__CourseStructure__Category__in=['DEC']).delete()
                for c_str in course_structure:
                    related_courses = courses.filter(CourseStructure_id=c_str.id)
                    if not related_courses or len(related_courses) < c_str.count:
                        slackCourses.append((c_str, related_courses))
                    elif len(related_courses) > c_str.count:
                        excessCourses.append((c_str, related_courses))
                    elif len(related_courses) == c_str.count:
                        for course in related_courses:
                            subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                            subject_row.save()
                if excessCourses:
                    excessCoursesDict = {c_str.id:[c_str.count, c_str.Category] for c_str, _ in excessCourses}
                    form = SubjectsSelectForm(excessCourses, event)
                    from json import dumps
                    return render(request, 'BTco_ordinator/BTSubjectsUpload.html',{'form':form, 'excess':dumps(excessCoursesDict)})
                msg=''
                if not slackCourses:
                    msg = 'Subjects uploaded successfully.'
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'form':form, 'slackCourses': slackCourses, 'msg':msg})
        elif request.POST.get('name') == 'SubjectsSelectForm':
            event = BTRegistrationStatus.objects.get(id=request.POST.get('event'))
            course_structure = BTCourseStructure.objects.filter(Regulation=event.Regulation, BYear=event.BYear, BSem=event.BSem, Dept=event.Dept)
            courses = BTCourses.objects.filter(CourseStructure_id__in=course_structure.values_list('id', flat=True))
            excessCourses = []
            slackCourses = []
            for c_str in course_structure:
                related_courses = courses.filter(CourseStructure_id=c_str.id)
                if len(related_courses) > c_str.count:
                        excessCourses.append((c_str, related_courses))
                elif len(related_courses) < c_str.count:
                    slackCourses.append((c_str, related_courses))
            form = SubjectsSelectForm(excessCourses, event, request.POST)
            if form.is_valid():
                for course_tup in excessCourses:
                    for course in course_tup[1]:
                        if form.cleaned_data.get('Check'+str(course.id)):
                            subject_row = BTSubjects_Staging(RegEventId_id=event.id, course_id=course.id)
                            subject_row.save()
                msg = ''
                if not slackCourses:
                    msg = 'Subjects uploaded successfully.'
                return render(request, 'BTco_ordinator/BTSubjectsUpload.html', {'slackCourses':slackCourses, 'msg':msg})
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
