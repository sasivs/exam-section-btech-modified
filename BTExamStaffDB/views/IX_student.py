from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render
from ADAUGDB.user_access_test import is_ExamStaff, ix_grade_student_status_access
from BTco_ordinator.models import BTFacultyAssignment, BTStudentRegistrations
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTHOD, BTCycleCoordinator
from BThod.models import BTCoordinator, BTFaculty_user
from BTExamStaffDB.forms import IXGradeStudentsAddition, IXGradeStudentsStatus
from BTExamStaffDB.models import BTIXGradeStudents

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
                student_registration = BTStudentRegistrations.objects.filter(RegEventId=regEvent, sub_id=subject, student__student__RegNo=regd_no).first()
                if BTIXGradeStudents.objects.filter(Registration=student_registration).exists():
                    BTIXGradeStudents.objects.filter(Registration=student_registration).update(Grade=grade)
                else:
                    ix_row = BTIXGradeStudents(Registration=student_registration, Grade=grade)
                    ix_row.save()
                msg = 'Student Grade Added Successfully.'
                return render(request, 'BTExamStaffDB/IXStudentAddition.html', {'form':form, 'msg':msg})
    else:
        form = IXGradeStudentsAddition()
    return render(request, 'BTExamStaffDB/IXStudentAddition.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(ix_grade_student_status_access)
def ix_student_status(request):
    msg = ''
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    students = None
    if 'Superintendent' in groups or 'ExamStaff' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Dept)
    elif 'Cycle-Co-ordinator' in groups:
        co_ordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=co_ordinator.Cycle)
    elif 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        faculty_assign = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
        regIDs = BTRegistrationStatus.objects.filter(id__in=faculty_assign.values_list('RegEventId_id', flat=True))
    if request.method == 'POST':
        form = IXGradeStudentsStatus(regIDs, request.POST)
        if request.POST.get('submit'):
            regEvent = request.POST.get('regId')
            if 'Faculty' in groups:
                students = BTIXGradeStudents.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id__in=faculty_assign.values_list('Subject_id', flat=True))
            else:
                students = BTIXGradeStudents.objects.filter(Registration__RegEventId=regEvent)
        elif request.POST.get('delete'):
            if 'ExamStaff' in groups:
                BTIXGradeStudents.objects.filter(id=request.POST.get('delete')).delete()
                regEvent = request.POST.get('regId')
                students = BTIXGradeStudents.objects.filter(Registration__RegEventId=regEvent)
                msg = 'Record Deleted Successfully.'
            else:
                raise Http404('You are not authorized to view this page')
    else:
        form = IXGradeStudentsStatus(regIDs)
    return render(request, 'BTExamStaffDB/IXGradeStudentsStatus.html', {'form':form, 'students':students, 'msg':msg})

