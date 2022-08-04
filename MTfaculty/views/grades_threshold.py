from pickle import NONE
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from MTsuperintendent.user_access_test import grades_threshold_access, grades_threshold_status_access
from MTfaculty.models import MTGradesThreshold, MTMarks_Staging
from MThod.models import MTFaculty_user, MTCoordinator
from MTco_ordinator.models import MTFacultyAssignment
from MTsuperintendent.models import MTGradePoints, MTHOD
from MTfaculty.forms import GradeThresholdForm, GradeThresholdStatusForm
import statistics as stat
from json  import dumps

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = MTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, Coordinator=faculty.Faculty).distinct('Subject')
    if not subjects:
        raise Http404('You are not allowed to add threshold marks')
    return render(request, 'MTfaculty/GradesThreshold.html', {'subjects': subjects})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold_assign(request, pk):
    subject_faculty = get_object_or_404(MTFacultyAssignment, id=pk)
    subject = subject_faculty.Subject
    grades = MTGradePoints.objects.filter(Regulation=subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R'])
    prev_thresholds = MTGradesThreshold.objects.filter(Subject=subject, RegEventId=subject_faculty.RegEventId)
    marks = MTMarks_Staging.objects.filter(Registration__RegEventId=subject_faculty.RegEventId.id, Registration__sub_id=subject.id)
    marks_list = marks.values_list('TotalMarks', flat=True)
    mean = round(stat.mean(marks_list), 2)
    stdev = round(stat.stdev(marks_list), 2)
    maximum = max(marks_list)
    if request.method == 'POST':
        form = GradeThresholdForm(subject_faculty, request.POST)
        if request.POST.get('submit-form'):
            if form.is_valid():
                if prev_thresholds:
                    # if (form.cleaned_data.get('uniform_grading')=='1' and prev_thresholds.first().uniform_grading) or \
                    #     (form.cleaned_data.get('uniform_grading')=='0' and not prev_thresholds.first().uniform_grading):
                    #     if form.cleaned_data.get('uniform_grading')=='1':
                    for grade in grades:
                        if form.cleaned_data[str(grade.id)]:
                            prev_thresholds.filter(Grade=grade).update(Threshold_Mark=int(form.cleaned_data[str(grade.id)]))
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
                    #                 threshold_mark = MTGradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                    #                     uniform_grading=True, Threshold_Mark=int(form.cleaned_data[str(grade.id)]))
                    #                 threshold_mark.save()
                    #     else:
                    #         section = form.cleaned_data.get('section')
                    #         for grade in grades:
                    #             if form.cleaned_data[section+str(grade.id)]:
                    #                 threshold_mark = MTGradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                    #                     uniform_grading=False, Section=section, \
                    #                         Threshold_Mark=int(form.cleaned_data[section+str(grade.id)]))
                    #                 threshold_mark.save()
                else:
                    # if form.cleaned_data.get('uniform_grading')=='1':
                    for grade in grades:
                        if form.cleaned_data[str(grade.id)]:
                            threshold_mark = MTGradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                Threshold_Mark=int(form.cleaned_data[str(grade.id)]))
                            threshold_mark.save()
                    # else:
                    #     section = form.cleaned_data.get('section')
                    #     for grade in grades:
                    #         if form.cleaned_data[section+str(grade.id)]:
                    #             threshold_mark = MTGradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                    #                 uniform_grading=False, Section=section, \
                    #                     Threshold_Mark=int(form.cleaned_data[section+str(grade.id)]))
                    #             threshold_mark.save()
                msg = 'Grades Threshold noted successfully'
                return render(request, 'MTfaculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'msg':msg})
        else:
            grades_data = [grade.Grade for grade in grades]
            no_of_students = {grade.Grade:0 for grade in grades}
            for index, grade in enumerate(grades):
                if request.POST.get(str(grade.id)):
                    no_of_students[grades_data[index]] = len(list(mark for mark in marks_list if mark>=int(request.POST.get(str(grade.id)))))
            for index in range(len(grades)-1, 0, -1):
                no_of_students[grades_data[index]] = no_of_students[grades_data[index]] - no_of_students[grades_data[index-1]]
            no_of_students = dumps(no_of_students)
            return render(request, 'MTfaculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'form':form, 'students':no_of_students, 'mean':mean, 'stdev':stdev, 'max':maximum})
    else:
        form = GradeThresholdForm(subject_faculty)
        no_of_students = None
        if prev_thresholds:
            grades_data = [grade.Grade for grade in grades]
            no_of_students = {grade.Grade:0 for grade in grades}
            for index, grade in enumerate(grades):
                if prev_thresholds.filter(Grade=grade.id):
                    threshold_mark = prev_thresholds.filter(Grade=grade.id).first().Threshold_Mark
                    no_of_students[grades_data[index]] = len(list(mark for mark in marks_list if mark>=threshold_mark))
            total = 0
            for index in range(len(grades)-1, 0, -1):
                no_of_students[grades_data[index]] = no_of_students[grades_data[index]] - no_of_students[grades_data[index-1]]
                total += no_of_students[grades_data[index]]
            no_of_students = dumps(no_of_students)
    return render(request, 'MTfaculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'form':form, 'students':no_of_students, 'mean':mean, 'stdev':stdev, 'max':maximum})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_status_access)
def grades_threshold_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    subjects = None
    if 'Faculty' in groups:
        faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1).distinct('Subject')
    elif 'Superintendent' in groups:
        subjects = MTFacultyAssignment.objects.filter(RegEventId__Status=1).distinct('Subject')
    elif 'Co-ordinator' in groups:
        co_ordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1).distinct('Subject')
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1).distinct('Subject')
    # elif 'Cycle-Co-ordinator' in groups:
    #     cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
    #     subjects = MTFacultyAssignment.objects.filter(RegEventId__Dept=cycle_cord.Cycle, RegEventId__MYear=1, RegEventId__Status=1).distinct('Subject')
    else:
        raise Http404('You are not allowed to view threshold marks')
    if request.method == 'POST':
        form = GradeThresholdStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = request.POST['subject'].split(':')[0]
            regEvent = request.POST['subject'].split(':')[1]
            thresholds = MTGradesThreshold.objects.filter(Subject_id=subject, RegEventId_id=regEvent)
            return render(request, 'MTfaculty/GradesThresholdStatus.html', {'form':form, 'thresholds':thresholds})
    else: 
        form = GradeThresholdStatusForm(subjects=subjects)
    return render(request, 'MTfaculty/GradesThresholdStatus.html', {'form':form})  
