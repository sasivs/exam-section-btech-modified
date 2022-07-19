from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from superintendent.user_access_test import grades_threshold_access, grades_threshold_status_access
from faculty.models import GradesThreshold
from hod.models import Faculty_user, Coordinator
from co_ordinator.models import FacultyAssignment
from superintendent.models import GradePoints, HOD, CycleCoordinator
from faculty.forms import GradeThresholdForm, GradeThresholdStatusForm


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, Coordinator=faculty.Faculty).distinct('Subject')
    if not subjects:
        raise Http404('You are not allowed to add threshold marks')
    return render(request, 'faculty/GradesThreshold.html', {'subjects': subjects})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold_assign(request, pk):
    subject_faculty = get_object_or_404(FacultyAssignment, id=pk)
    subject = subject_faculty.Subject
    grades = GradePoints.objects.filter(Regulation=subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R'])
    prev_thresholds = GradesThreshold.objects.filter(Subject=subject, RegEventId=subject_faculty.RegEventId)
    if request.method == 'POST':
        form = GradeThresholdForm(subject_faculty, request.POST)
        if form.is_valid():
            if request.POST.get('submit-form'):
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
                            threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                uniform_grading=True, Threshold_Mark=int(form.cleaned_data[str(grade.id)]))
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
                return render(request, 'faculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'msg':msg})

    else:
        form = GradeThresholdForm(subject_faculty)
    return render(request, 'faculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'form':form})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_status_access)
def grades_threshold_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    subjects = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1).distinct('Subject')
    elif 'Superintendent' in groups:
        subjects = FacultyAssignment.objects.filter(RegEventId__Status=1).distinct('Subject')
    elif 'Co-ordinator' in groups:
        co_ordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1).distinct('Subject')
    elif 'HOD' in groups:
        hod = HOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1).distinct('Subject')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(RegEventId__Dept=cycle_cord.Cycle, RegEventId__BYear=1, RegEventId__Status=1).distinct('Subject')
    else:
        raise Http404('You are not allowed to view threshold marks')
    if request.method == 'POST':
        form = GradeThresholdStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = request.POST['subject'].split(':')[0]
            regEvent = request.POST['subject'].split(':')[1]
            thresholds = GradesThreshold.objects.filter(Subject_id=subject, RegEventId_id=regEvent)
            return render(request, 'faculty/GradesThresholdStatus.html', {'form':form, 'thresholds':thresholds})
    else: 
        form = GradeThresholdStatusForm(subjects=subjects)
    return render(request, 'faculty/GradesThresholdStatus.html', {'form':form})  
