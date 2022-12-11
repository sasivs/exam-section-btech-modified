from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import is_Hod
from django.shortcuts import render
from ADAUGDB.models import BTHOD, BTRegistrationStatus
from BTExamStaffDB.models import BTStudentInfo
from BThod.forms import DeptStudentStatusForm, StudentHistoryForm
from BTfaculty.models import BTMarks, BTStudentGrades
from BTco_ordinator.models import BTDroppedRegularCourses, BTNotPromoted, BTFacultyAssignment

@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def student_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'HOD' in groups:
        dept = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first().Dept
    if request.method == 'POST':
        form = DeptStudentStatusForm(request.POST)
        if form.is_valid():
            admyear = form.cleaned_data.get('AdmYear')
            student_info = BTStudentInfo.objects.filter(AdmissionYear=admyear, Dept=dept)
            return render(request, 'BThod/StudentStatus.html', {'form':form, 'students':student_info})
    else:
        form = DeptStudentStatusForm()
    return render(request, 'BThod/StudentStatus.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def student_history(request, pk):
    student = BTStudentInfo.objects.get(id=pk)
    dropped_courses = BTDroppedRegularCourses.objects.filter(student__RegNo=student.RegNo, Registered=False)
    not_promoted = BTNotPromoted.objects.filter(student__RegNo=student.RegNo)
    if request.method == 'POST':
        form = StudentHistoryForm(student, request.POST)
        if request.POST.get('Submit'):
            if form.is_valid():
                event = form.cleaned_data('event')
                event = BTRegistrationStatus.objects.get(id=event)
                marks_list = BTMarks.objects.filter(Registration__RegEventId_id=event.id)
                grades_list = BTStudentGrades.objects.filter(RegId__RegEventId_id=event.id)
                faculty = BTFacultyAssignment.objects.filter(RegEventId_id=event.id)
                for rindex, mark in enumerate(marks_list):
                    mark.s_no = rindex+1
                    mark.grade = grades_list.filter(RegId=mark.Registration).first().Grade
                    mark.faculty = faculty.filter(Subject__id=mark.Registration.sub_id_id, Section=mark.Registration.student.Section).first().Faculty
                return render(request, 'BThod/StudentHistory.html', {'form': form, 'student':student, 'marks_list':marks_list})
    else:
        form = StudentHistoryForm(student)
    return render(request, 'BThod/StudentHistory.html', {'form':form, 'student':student, 'dropped_courses':dropped_courses, 'not_promoted':not_promoted})