from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from ADAUGDB.user_access_test import grades_threshold_access, grades_threshold_status_access
from BTfaculty.models import BTGradesThreshold, BTMarks_Staging
from BThod.models import BTFaculty_user, BTCoordinator
from BTco_ordinator.models import BTFacultyAssignment, BTSubjects
from ADAUGDB.models import BTGradePoints, BTHOD, BTCycleCoordinator
from BTfaculty.forms import GradeThresholdForm, GradeThresholdStatusForm
from ADAUGDB.models import BTRegistrationStatus
from json import dumps
import statistics as stat
from import_export.formats.base_formats import XLSX
import pandas as pd
from django.db import transaction
from django.db.models import Q

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, Coordinator=faculty.Faculty).distinct('Subject','RegEventId_id')
    oe_subjects = subjects.filter(Subject__course__CourseStructure__Category__in=['OEC', 'OPC']).distinct('Subject__course__SubCode')
    for sub in oe_subjects:
        id_string = '?'.join(list(map(str, subjects.filter(Subject__course__CourseStructure__Category__in=['OEC', 'OPC'], Subject__course__SubCode=sub.Subject.course.SubCode).values_list('id', flat=True))))
        sub.id = id_string
        sub.RegEventId_open = sub.RegEventId.__open_str__()
        subjects = subjects.filter(Subject__course__CourseStructure__Category__in=['OEC', 'OPC']).exclude(~Q(id=sub.id), Subject__course__SubCode=sub.Subject.course.SubCode)
    if not subjects:
        raise Http404('You are not allowed to add threshold marks')
    return render(request, 'BTfaculty/GradesThreshold.html', {'subjects': subjects, 'oe_subjects':oe_subjects})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold_assign(request, pk):
    subject_faculty = BTFacultyAssignment.objects.filter(id__in=pk.split('?'))
    subjects = subject_faculty.all().values_list('Subject_id', flat=True)
    regEventIds = subject_faculty.all().values_list('RegEventId_id', flat=True)
    subject = subject_faculty[0].Subject
    grades = BTGradePoints.objects.filter(Regulation=subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R','W'])
    # prev_thresholds = BTGradesThreshold.objects.filter(Subject=subject, RegEventId=subject_faculty[0].RegEventId)
    marks = BTMarks_Staging.objects.filter(Registration__RegEventId_id__in=regEventIds, Registration__sub_id_id__in=subjects)
    promote_thresholds = subject.course.MarkDistribution.PromoteThreshold
    promote_thresholds = promote_thresholds.split(',')
    promote_thresholds = [thr.split('+') for thr in promote_thresholds]
    failed_marks_objs = BTMarks_Staging.objects.none()
    for mark in marks:
        if mark.Registration.Mode == 1:
            marks_list = mark.Marks.split(',')
            marks_list = [m.split('+') for m in marks_list]
            failed = False
            for outer_index in range(len(promote_thresholds)):
                for inner_index in range(len(promote_thresholds[outer_index])):
                    if float(marks_list[outer_index][inner_index]) < float(promote_thresholds[outer_index][inner_index]):
                        failed_marks_objs |= marks.filter(id=mark.id)
                        failed = True
                        break
                if failed:
                    break
    marks = marks.exclude(id__in=failed_marks_objs.values_list('id', flat=True))
    marks_list = marks.values_list('TotalMarks', flat=True)
    if len(marks_list)>1:
        mean = round(stat.mean(marks_list), 2)
        stdev = round(stat.stdev(marks_list), 2)
        maximum = max(marks_list)
    elif len(marks_list) == 1:
        mean = marks_list[0]
        stdev = marks_list[0]
        maximum = marks_list[0]
    else:
        mean = 0
        stdev = 0
        maximum = 0
    if request.method == 'POST':
        form = GradeThresholdForm(subject_faculty, request.POST)
        if request.POST.get('submit-form'):
            if form.is_valid():
                for sub in subject_faculty:
                    prev_thresholds = BTGradesThreshold.objects.filter(Subject=sub, RegEventId=sub.RegEventId)
                    if prev_thresholds:
                    # if (form.cleaned_data.get('uniform_grading')=='1' and prev_thresholds.first().uniform_grading) or \
                    #     (form.cleaned_data.get('uniform_grading')=='0' and not prev_thresholds.first().uniform_grading):
                    #     if form.cleaned_data.get('uniform_grading')=='1':
                        for grade in grades:
                            if form.cleaned_data[str(grade.id)]:
                                prev_thresholds.filter(Grade=grade, Exam_Mode=False).update(Threshold_Mark=float(form.cleaned_data[str(grade.id)]))
                        
                        exam_mode_grade = grades.filter(Grade__in=['P','F'])
                        for grade in exam_mode_grade:
                            if form.cleaned_data[str('exam_mode_')+str(grade.id)]:
                                prev_thresholds.filter(Grade=grade, Exam_Mode=True).update(Threshold_Mark=float(form.cleaned_data[str('exam_mode_')+str(grade.id)]))
                        # else:
                        #     section = form.cleaned_data.get('section')
                        #     for grade in grades:
                        #         if form.cleaned_data[section+str(grade.id)]:
                        #             prev_thresholds.filter(Grade=grade, Section=section).update(Threshold_Mark=int(form.cleaned_data[section+str(grade.id)]))
                    # else:
                    #     prev_thresholds.delete()
                    #     if form.cleaned_data.get('uniform_grading')=='1':
                    #         for grade in grades:
                    #             if form.cleaned_data[str(grade.id)]:
                    #                 threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                    #                     uniform_grading=True, Threshold_Mark=int(form.cleaned_data[str(grade.id)]))
                    #                 threshold_mark.save()
                    #     else:
                    #         section = form.cleaned_data.get('section')
                    #         for grade in grades:
                    #             if form.cleaned_data[section+str(grade.id)]:
                    #                 threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                    #                     uniform_grading=False, Section=section, \
                    #                         Threshold_Mark=int(form.cleaned_data[section+str(grade.id)]))
                    #                 threshold_mark.save()
                    else:
                        # if form.cleaned_data.get('uniform_grading')=='1':
                        for grade in grades:
                            if form.cleaned_data[str(grade.id)]:
                                threshold_mark = BTGradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                    Threshold_Mark=float(form.cleaned_data[str(grade.id)]), Exam_Mode=False)
                                threshold_mark.save()
                        exam_mode_grade = grades.filter(Grade__in=['P','F'])
                        for grade in exam_mode_grade:
                            if form.cleaned_data[str('exam_mode_')+str(grade.id)]:
                                threshold_mark = BTGradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                        Threshold_Mark=float(form.cleaned_data[str('exam_mode_')+str(grade.id)]), Exam_Mode=True)
                                threshold_mark.save()

                    # else:
                    #     section = form.cleaned_data.get('section')
                    #     for grade in grades:
                    #         if form.cleaned_data[section+str(grade.id)]:
                    #             threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                    #                 uniform_grading=False, Section=section, \
                    #                     Threshold_Mark=int(form.cleaned_data[section+str(grade.id)]))
                    #             threshold_mark.save()
                msg = 'Grades Threshold noted successfully'
                return render(request, 'BTfaculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'msg':msg})
        else:
            grades = grades.exclude(Grade='F')
            grades_data = [grade.Grade for grade in grades]
            no_of_students = {grade.Grade:0 for grade in grades}
            passed_marks_objs = BTMarks_Staging.objects.none()
            for index, grade in enumerate(grades):
                if request.POST.get(str(grade.id)):
                    passed_marks_objs = passed_marks_objs.union(marks.filter(TotalMarks__gte=float(request.POST.get(str(grade.id)))))
                    no_of_students[grades_data[index]] = len(list(mark for mark in marks_list if mark>=float(request.POST.get(str(grade.id)))))
            passed_marks_list = passed_marks_objs.values_list('TotalMarks', flat=True)
            if len(passed_marks_list)>1:
                mean = round(stat.mean(passed_marks_list), 2)
                stdev = round(stat.stdev(passed_marks_list), 2)
                maximum = max(passed_marks_list)
            elif len(passed_marks_list) == 1:
                mean = passed_marks_list[0]
                stdev = passed_marks_list[0]
                maximum = passed_marks_list[0]
            else:
                mean = 0
                stdev = 0
                maximum = 0
            for index in range(len(grades)-1, 0, -1):
                no_of_students[grades_data[index]] = no_of_students[grades_data[index]] - no_of_students[grades_data[index-1]]
            no_of_students = dumps(no_of_students)
            return render(request, 'BTfaculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'form':form, 'students':no_of_students, 'mean':mean, 'stdev':stdev, 'max':maximum})


    else:
        form = GradeThresholdForm(subject_faculty)
        no_of_students = None
        prev_thresholds = BTGradesThreshold.objects.filter(Subject=subject, RegEventId=subject_faculty[0].RegEventId)
        if prev_thresholds:
            grades = grades.exclude(Grade='F')
            grades_data = [grade.Grade for grade in grades]
            no_of_students = {grade.Grade:0 for grade in grades}
            passed_marks_objs = BTMarks_Staging.objects.none()
            for index, grade in enumerate(grades):
                if prev_thresholds.filter(Grade=grade.id):
                    threshold_mark = prev_thresholds.filter(Grade=grade.id).first().Threshold_Mark
                    passed_marks_objs = passed_marks_objs.union(marks.filter(TotalMarks__gte=threshold_mark))
                    no_of_students[grades_data[index]] = len(list(mark for mark in marks_list if mark>=threshold_mark))
            total = 0
            passed_marks_list = passed_marks_objs.values_list('TotalMarks', flat=True)
            if len(passed_marks_list)>1:
                mean = round(stat.mean(passed_marks_list), 2)
                stdev = round(stat.stdev(passed_marks_list), 2)
                maximum = max(passed_marks_list)
            elif len(passed_marks_list) == 1:
                mean = passed_marks_list[0]
                stdev = passed_marks_list[0]
                maximum = passed_marks_list[0]
            else:
                mean = 0
                stdev = 0
                maximum = 0
            for index in range(len(grades)-1, 0, -1):
                no_of_students[grades_data[index]] = no_of_students[grades_data[index]] - no_of_students[grades_data[index-1]]
                total += no_of_students[grades_data[index]]
            no_of_students = dumps(no_of_students)
    return render(request, 'BTfaculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'form':form,  'students':no_of_students, 'mean':mean, 'stdev':stdev, 'max':maximum})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_status_access)
def grades_threshold_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    subjects = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1).distinct('Subject','RegEventId_id')
    elif 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1).distinct('Subject','RegEventId_id')
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1).distinct('Subject','RegEventId_id')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1).distinct('Subject','RegEventId_id')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Dept=cycle_cord.Cycle, RegEventId__BYear=1, RegEventId__Status=1).distinct('Subject','RegEventId_id')
    else:
        raise Http404('You are not allowed to view threshold marks')
    if request.method == 'POST':
        form = GradeThresholdStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = request.POST['subject'].split(':')[0].split(',')[0]
            regEvent = request.POST['subject'].split(':')[1].split(',')[0]
            thresholds = BTGradesThreshold.objects.filter(Subject_id=subject, RegEventId_id=regEvent)
            return render(request, 'BTfaculty/GradesThresholdStatus.html', {'form':form, 'thresholds':thresholds})
    else: 
        form = GradeThresholdStatusForm(subjects=subjects)
    return render(request, 'BTfaculty/GradesThresholdStatus.html', {'form':form})  

def add_grades_threshold(file):
    file = pd.read_excel(file)
    error_rows=[]
    for rIndex, row in file.iterrows():
        print(str(row['Dept'])+':'+row['SubCode'])
        fac_assign_objs = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, RegEventId__AYear=row['AYear'], RegEventId__ASem=row['ASem'], RegEventId__BYear=row['BYear'], RegEventId__BSem=row['BSem'], \
            RegEventId__Dept=row['Dept'], RegEventId__Regulation=row['Regulation'], RegEventId__Mode=row['Mode'], Subject__course__SubCode=row['SubCode'])
        for fac_assign_obj in fac_assign_objs:
            study_grades = BTGradePoints.objects.filter(Regulation=fac_assign_obj.Subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R','W'])
            index = 8
            for grade in study_grades:
                if row[index] >= 0:
                    if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=grade, Exam_Mode=False).exists():
                        grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=grade, Threshold_Mark=row[index], Exam_Mode=False)
                        grades_threshold_row.save()
                    else:
                        BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=grade, Exam_Mode=False).update(Threshold_Mark=row[index])
                else:
                    error_rows.append(row)
                index += 1
            
            exam_grades = BTGradePoints.objects.filter(Regulation=fac_assign_obj.Subject.RegEventId.Regulation, Grade__in=['P','F'])

            if fac_assign_obj.Subject.RegEventId.Regulation == 1:
                p_threshold = 15
                f_threshold = 0
            else:
                p_threshold = 17.5
                f_threshold = 0
            if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='P').first(), Exam_Mode=True).exists():
                grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='P').first(), Threshold_Mark=row[index], Exam_Mode=True)
                grades_threshold_row.save()
                index+=1
            if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='F').first(), Exam_Mode=True).exists():
                grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='F').first(), Threshold_Mark=row[index], Exam_Mode=True)
                grades_threshold_row.save()
    print("Errors")
    for er in error_rows:
        print('Error'+ er['SubCode'])

    return "Completed!!"
