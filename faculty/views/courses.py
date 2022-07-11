from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from co_ordinator.models import FacultyAssignment
from hod.models import Faculty_user 
from superintendent.user_access_test import grades_threshold_access


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def courses_assigned(request):
    user = request.user
    faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True)
    subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    return render(request, 'faculty/CoursesAssigned.html', {'subjects':subjects})
