from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from superintendent.user_access_test import grades_threshold_access, grades_status_access
from superintendent.models import BTRegistrationStatus, BTHOD
from hod.models import BTFaculty_user, BTCoordinator
from BTco_ordinator.models import BTFacultyAssignment, BTRollLists, BTStudentRegistrations
from faculty.models import BTAttendance_Shortage, BTGradesThreshold, BTMarks_Staging, BTStudentGrades_Staging
from ExamStaffDB.models import BTIXGradeStudents
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
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1, RegEventId__GradeStatus=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            regEvent = BTRegistrationStatus.objects.get(id=regEvent)
            section = form.cleaned_data.get('subject').split(':')[2]

            roll_list = BTRollLists.objects.filter(RegEventId=regEvent, Section=section)

            marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId=regEvent.id, Registration__sub_id=subject, \
                Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True))

            attendance_shortage = BTAttendance_Shortage.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
            grades_objects = BTStudentGrades_Staging.objects.filter(RegId__in=marks_objects.values_list('Registration', flat=True))
            
            for att in attendance_shortage:
                if grades_objects.filter(RegId=att.Registration.id):
                    grades_objects.filter(RegId=att.Registration.id).update(Grade='R', AttGrade='X')
                else:
                    grade = BTStudentGrades_Staging(RegId=att.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                        Grade='R', AttGrade='X') 
                    grade.save()
                mark_obj = marks_objects.filter(Registration__RegNo=att.Student.RegNo).first()
                marks_objects = marks_objects.exclude(mark_obj)
            
            ix_grades = BTIXGradeStudents.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))

            for ix_grade in ix_grades:
                if grades_objects.filter(RegId=ix_grade.Registration.id):
                    grades_objects.filter(RegId=ix_grade.Registration.id).update(Grade=ix_grade.Grade, AttGrade='P')
                else:
                    grade = BTStudentGrades_Staging(RegId=ix_grade.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                        Grade=ix_grade.Grade, AttGrade='P')
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=ix_grade.Registration)
            
            if BTGradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent).exists():
                thresholds = BTGradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent).order_by('-Threshold_Mark')
            
            if not thresholds:
                msg = 'Grade Threshold is not updated for this subject.'
                return render(request, 'faculty/GradesGenerate.html', {'form':form, 'msg':msg})

            for mark in marks_objects:
                for threshold in thresholds:
                    if mark.TotalMarks >= threshold.Threshold_Mark:
                        if grades_objects.filter(RegId=mark.Registration.id):
                            grades_objects.filter(RegId=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='P')
                            break
                        else:
                            grade = BTStudentGrades_Staging(RegId=mark.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                                Grade=threshold.Grade.Grade, AttGrade='P')
                            grade.save()
                            break
            
            msg = 'Grades generated successfully.'
            return render(request, 'faculty/GradesGenerate.html', {'form':form, 'msg':msg})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'faculty/GradesGenerate.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(grades_status_access)
def grades_status(request):
    
    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    subjects = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    elif 'Superintendent' in groups:
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            regEvent = BTRegistrationStatus.objects.get(id=regEvent)
            section = form.cleaned_data.get('subject').split(':')[2]
            roll_list = BTRollLists.objects.filter(RegEventId=regEvent, Section=section)
            student_registrations = BTStudentRegistrations.objects.filter(RegEventId=regEvent.id, sub_id=subject, \
                RegNo__in=roll_list.values_list('student__RegNo', flat=True))
            grades = BTStudentGrades_Staging.objects.filter(RegEventId=regEvent.id, RegId__in=student_registrations.values_list('id',flat=True))
            grades = list(grades)
            for grade in grades:
                grade.RegNo = student_registrations.filter(id=grade.RegId).first().RegNo
                grade.regEvent = regEvent.__str__()
                grade.Marks = BTMarks_Staging.objects.filter(Registration_id=grade.RegId).first().TotalMarks
            import operator
            grades = sorted(grades, key=operator.attrgetter('RegNo'))
            return render(request, 'faculty/GradesStatus.html', {'form':form, 'grades':grades})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'faculty/GradesStatus.html', {'form':form})