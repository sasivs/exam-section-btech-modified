from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from SupExamDBRegistrations.user_access_test import grades_threshold_access
from SupExamDBRegistrations.models import RegistrationStatus, RollLists, StudentGrades_Staging, StudentRegistrations
from hod.models import Faculty_user
from co_ordinator.models import FacultyAssignment
from faculty.models import Attendance_Shortage, GradesThreshold, Marks
from superintendent.models import IXGradeStudents
from faculty.forms import MarksStatusForm


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_generate(request):

    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty, RevokeDate__isnull=True)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            regEvent = RegistrationStatus.objects.get(id=regEvent)
            section = form.cleaned_data.get('subject').split(':')[2]

            roll_list = RollLists.objects.filter(RegEventId=regEvent, Section=section)

            marks_objects = Marks.objects.filter(Registration__RegEventId=regEvent.id, Registration__sub_id=subject, \
                Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True))

            attendance_shortage = Attendance_Shortage.objects.filter(RegEventId_id=regEvent.id, Subject_id=subject, Student__in=roll_list.values_list('student', flat=True))
            
            for att in attendance_shortage:
                mark_obj = marks_objects.filter(Registration__RegNo=att.Student.RegNo).first()
                grade = StudentGrades_Staging(RegId=mark_obj.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                    Grade='R', AttGrade='X') 
                grade.save()
                marks_objects = marks_objects.exclude(mark_obj)
            
            ix_grades = IXGradeStudents.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))

            for ix_grade in ix_grades:
                grade = StudentGrades_Staging(RegId=ix_grade.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                    Grade=ix_grade.Grade, AttGrade='P')
                grade.save()
                marks_objects = marks_objects.exclude(Registration=ix_grade.Registration)
            
            if GradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent, uniform_grading=True).exists():
                thresholds = GradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent, uniform_grading=True).order_by('-ThresholdMark')
            else:
                thresholds = GradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent, unifrom_grading=False, Section=section).order_by('-ThresholdMark')

            for mark in marks_objects:
                for threshold in thresholds:
                    if mark.TotalMarks >= threshold.ThresholdMark:
                        grade = StudentGrades_Staging(RegId=mark.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                            Grade=threshold.Grade, AttGrade='P')
                        grade.save()
            
            msg = 'Grades generated successfully.'
            return render(request, 'faculty/GradesGenerate.html', {'form':form, 'msg':msg})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'faculty/GradesGenerate.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def grades_status(request):
    
    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty, RevokeDate__isnull=True)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        subject = form.cleaned_data.get('subject').split(':')[0]
        regEvent = form.cleaned_data.get('subject').split(':')[1]
        regEvent = RegistrationStatus.objects.get(id=regEvent)
        section = form.cleaned_data.get('subject').split(':')[2]
        roll_list = RollLists.objects.filter(RegEventId=regEvent, Section=section)
        student_registrations = StudentRegistrations.objects.filter(RegEventId=regEvent.id, sub_id=subject, \
            RegNo__in=roll_list.values_list('student__RegNo', flat=True))
        grades = StudentGrades_Staging.objects.filter(RegEventId=regEvent.id, RegId__in=student_registrations.values_list('id',flat=True))
        for grade in grades:
            grade.RegNo = student_registrations.filter(id=grade.RegId).first().RegNo
            grade.regEvent = regEvent.__str__()
        return render(request, 'faculty/GradesStatus.html', {'form':form, 'grades':grades})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'faculty/GradesStatus.html', {'form':form})