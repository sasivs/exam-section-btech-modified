from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render
from MTsuperintendent.user_access_test import is_ExamStaff, ix_grade_student_status_access
from MTco_ordinator.models import MTStudentRegistrations, MTFacultyAssignment
from MTsuperintendent.models import MTRegistrationStatus, MTHOD
from MThod.models import MTCoordinator, MTFaculty_user
from MTExamStaffDB.forms import IXGradeStudentsAddition, IXGradeStudentsStatus
from MTExamStaffDB.models import MTIXGradeStudents

@login_required(login_url="/login/")
@user_passes_test(is_ExamStaff)
def ix_student_assignment(request):
    if request.method == 'POST':
        form = IXGradeStudentsAddition(request.POST)
        if form.is_valid():
            if request.POST.get('submit-form'):
                regEvent = form.cleaned_data.get('regId')
                subject = form.cleaned_data.get('subject')
                regd_no = form.cleaned_data.get('regd_no')
                grade = form.cleaned_data.get('grade')
                student_registration = MTStudentRegistrations.objects.filter(RegEventId=regEvent, sub_id=subject, RegNo=regd_no).first()
                if MTIXGradeStudents.objects.filter(Registration=student_registration).exists():
                    MTIXGradeStudents.objects.filter(Registration=student_registration).update(Grade=grade)
                else:
                    ix_row = MTIXGradeStudents(Registration=student_registration, Grade=grade)
                    ix_row.save()
                msg = 'Student Grade Added Successfully.'
                return render(request, 'ExamStaffDB/IXStudentAddition.html', {'form':form, 'msg':msg})
    else:
        form = IXGradeStudentsAddition()
    return render(request, 'ExamStaffDB/IXStudentAddition.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(ix_grade_student_status_access)
def ix_student_status(request):
    msg = ''
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    students = None
    if 'Superintendent' in groups or 'ExamStaff' in groups:
        regIDs = MTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept)
    elif 'Co-ordinator' in groups:
        co_ordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept)
    elif 'Faculty' in groups:
        faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        faculty_assign = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
        regIDs = MTRegistrationStatus.objects.filter(id__in=faculty_assign.values_list('RegEventId_id', flat=True))
    if request.method == 'POST':
        form = IXGradeStudentsStatus(regIDs, request.POST)
        if request.POST.get('submit'):
            regEvent = request.POST.get('regId')
            students = MTIXGradeStudents.objects.filter(Registration__RegEventId=regEvent)
        elif request.POST.get('delete'):
            if 'ExamStaff' in groups:
                MTIXGradeStudents.objects.filter(id=request.POST.get('delete')).delete()
                regEvent = request.POST.get('regId')
                students = MTIXGradeStudents.objects.filter(Registration__RegEventId=regEvent)
                msg = 'Record Deleted Successfully.'
            else:
                raise Http404('You are not authorized to view this page')
    else:
        form = IXGradeStudentsStatus(regIDs)
    return render(request, 'ExamStaffDB/IXGradeStudentsStatus.html', {'form':form, 'students':students, 'msg':msg})

