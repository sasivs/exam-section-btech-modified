from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from MTsuperintendent.user_access_test import grades_threshold_access, grades_status_access
from MTsuperintendent.models import MTRegistrationStatus, MTHOD
from MThod.models import MTFaculty_user, MTCoordinator
from MTco_ordinator.models import MTFacultyAssignment, MTRollLists, MTStudentRegistrations
from MTfaculty.models import MTAttendance_Shortage, MTGradesThreshold, MTMarks_Staging, MTStudentGrades_Staging
from MTExamStaffDB.models import MTIXGradeStudents
from MTfaculty.forms import MarksStatusForm


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
        faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1, RegEventId__GradeStatus=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            regEvent = MTRegistrationStatus.objects.get(id=regEvent)

            roll_list = MTRollLists.objects.filter(RegEventId=regEvent)

            marks_objects = MTMarks_Staging.objects.filter(Registration__RegEventId=regEvent.id, Registration__sub_id=subject, \
                Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True))

            attendance_shortage = MTAttendance_Shortage.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
            grades_objects = MTStudentGrades_Staging.objects.filter(RegId__in=marks_objects.values_list('Registration', flat=True))
            
            for att in attendance_shortage:
                if grades_objects.filter(RegId=att.Registration.id):
                    grades_objects.filter(RegId=att.Registration.id).update(Grade='R', AttGrade='X')
                else:
                    grade = MTStudentGrades_Staging(RegId=att.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                        Grade='R', AttGrade='X') 
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=att.Registration)
            
            ix_grades = MTIXGradeStudents.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))

            for ix_grade in ix_grades:
                if grades_objects.filter(RegId=ix_grade.Registration.id):
                    grades_objects.filter(RegId=ix_grade.Registration.id).update(Grade=ix_grade.Grade, AttGrade='P')
                else:
                    grade = MTStudentGrades_Staging(RegId=ix_grade.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                        Grade=ix_grade.Grade, AttGrade='P')
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=ix_grade.Registration)
            
            if MTGradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent).exists():
                thresholds = MTGradesThreshold.objects.filter(Subject_id=subject, RegEventId=regEvent).order_by('-Threshold_Mark')


            if not thresholds:
                msg = 'Grade Threshold is not updated for this subject.'
                return render(request, 'MTfaculty/GradesGenerate.html', {'form':form, 'msg':msg})

            for mark in marks_objects:
                for threshold in thresholds:
                    if mark.TotalMarks >= threshold.Threshold_Mark:
                        if grades_objects.filter(RegId=mark.Registration.id):
                            grades_objects.filter(RegId=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='P')
                            break
                        else:
                            grade = MTStudentGrades_Staging(RegId=mark.Registration.id, RegEventId=regEvent.id, Regulation=regEvent.Regulation, \
                                Grade=threshold.Grade.Grade, AttGrade='P')
                            grade.save()
                            break
            
            msg = 'Grades generated successfully.'
            return render(request, 'MTfaculty/GradesGenerate.html', {'form':form, 'msg':msg})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'MTfaculty/GradesGenerate.html', {'form':form})


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
        faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    elif 'Superintendent' in groups:
        subjects = MTFacultyAssignment.objects.filter(RegEventId__Status=1)
    elif 'Co-ordinator' in groups:
        co_ordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1)
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            regEvent = MTRegistrationStatus.objects.get(id=regEvent)
            roll_list = MTRollLists.objects.filter(RegEventId=regEvent)
            student_registrations = MTStudentRegistrations.objects.filter(RegEventId=regEvent.id, sub_id=subject, \
                RegNo__in=roll_list.values_list('student__RegNo', flat=True))
            grades = MTStudentGrades_Staging.objects.filter(RegEventId=regEvent.id, RegId__in=student_registrations.values_list('id',flat=True))
            grades = list(grades)
            for grade in grades:
                grade.RegNo = student_registrations.filter(id=grade.RegId).first().RegNo
                grade.regEvent = regEvent.__str__()
                grade.Marks = MTMarks_Staging.objects.filter(Registration_id=grade.RegId).first().TotalMarks
            import operator
            grades = sorted(grades, key=operator.attrgetter('RegNo'))
            return render(request, 'MTfaculty/GradesStatus.html', {'form':form, 'grades':grades})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'MTfaculty/GradesStatus.html', {'form':form})