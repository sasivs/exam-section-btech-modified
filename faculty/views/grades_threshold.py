from django.contrib.auth.decorators import login_required, user_passes_test 
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from SupExamDBRegistrations.user_access_test import grades_threshold_access
from faculty.models import GradesThreshold
from hod.models import Faculty_user
from co_ordinator.models import FacultyAssignment
from SupExamDBRegistrations.models import GradePoints, RollLists, StudentRegistrations
from faculty.forms import GradeThresholdForm, GradeThresholdStatusForm


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    if not faculty.Faculty.Coordinator:
        raise Http404('You are not allowed to add threshold marks')
    subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    return render(request, 'faculty/GradesThreshold.html', {'subjects', subjects})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold_assign(request, pk):
    subject_faculty = get_object_or_404(FacultyAssignment, id=pk)
    subject = subject_faculty.Subject
    grades = GradePoints.objects.filter(Regulation=subject.RegEventId.Regulation)
    prev_thresholds = GradesThreshold.objects.filter(subject=subject, RegEventId=subject_faculty.RegEventId)
    student_registrations = StudentRegistrations.objects.filter(RegEventId=subject_faculty.RegEventId.id, sub_id=subject_faculty.Subject.id)
    sections = RollLists.objects.filter(RegEventId=subject_faculty.RegEventId, regd_no__in=student_registrations.values_list('regd_no', flat=True)).values_list('Section', flat=True).distinct()
    if request.method == 'POST':
        form = GradeThresholdForm(subject_faculty, request.POST)
        if form.is_valid():
            if form.cleaned_data.get('submit'):
                if prev_thresholds:
                    if form.cleaned_data.get('uniform_grading') == prev_thresholds.first().uniform_grading:
                        if form.cleaned_data.get('uniform_grading'):
                            for grade in grades:
                                if form.cleaned_data[grade.id]:
                                    prev_thresholds.filter(Grade=grade).update(Threshold_Mark=form.cleaned_data[grade.id])
                        else:
                            for section in sections:
                                for grade in grades:
                                    if form.cleaned_data[str(grade.id)+'_'+str(section)]:
                                        prev_thresholds.filter(Grade=grade, Section=section).update(Threshold_Mark=form.cleaned_data[str(grade.id)+'_'+str(section)])
                    else:
                        prev_thresholds.delete()
                        if form.cleaned_data.get('uniform_grading'):
                            for grade in grades:
                                if form.cleaned_data[grade.id]:
                                    threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                        uniform_grading=form.cleaned_data.get('uniform_grading'), Threshold_Mark=form.cleaned_data[grade.id])
                                    threshold_mark.save()
                        else:
                            for section in sections:
                                for grade in grades:
                                    if form.cleaned_data[str(grade.id)+'_'+str(section)]:
                                        threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                            uniform_grading=form.cleaned_data.get('uniform_grading'), Section=section, \
                                                Threshold_Mark=form.cleaned_data[str(grade.id)+'_'+str(section)])
                                        threshold_mark.save()
                else:
                    if form.cleaned_data.get('uniform_grading'):
                        for grade in grades:
                            if form.cleaned_data[grade.id]:
                                threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                    uniform_grading=form.cleaned_data.get('uniform_grading'), Threshold_Mark=form.cleaned_data[grade.id])
                                threshold_mark.save()
                    else:
                        for section in sections:
                            for grade in grades:
                                if form.cleaned_data[str(grade.id)+'_'+str(section)]:
                                    threshold_mark = GradesThreshold(Grade=grade, Subject=subject, RegEventId=subject_faculty.RegEventId, \
                                        uniform_grading=form.cleaned_data.get('uniform_grading'), Section=section, \
                                            Threshold_Mark=form.cleaned_data[str(grade.id)+'_'+str(section)])
                                    threshold_mark.save()
                msg = 'Grades Threshold noted successfully'
                return render(request, 'faculty/GradesThresholdAssign.html', {'subject':subject_faculty, 'form':form, 'msg':msg})

    else:
        form = GradeThresholdForm(subject=subject_faculty)
    return render(request, 'faculty/GradeThresholdAssign.html', {'subject':subject_faculty, 'form':form})

@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_threshold_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    if not faculty.Faculty.Coordinator:
        raise Http404('You are not allowed to view threshold marks')
    subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)  
    if request.method == 'POST':
        form = GradeThresholdStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = request.POST['subject'].split(':')[0]
            regEvent = request.POST['subject'].split(':')[1]
            thresholds = GradesThreshold.objects.filter(subject_id=subject, RegEventId_id=regEvent)
            return render(request, 'faculty/GradesThresholdStatus.html', {'form':form, 'thresholds':thresholds})  
    form = GradeThresholdStatusForm(subjects=subjects)
    return render(request, 'faculty/GradesThresholdStatus.html', {'form':form})  
