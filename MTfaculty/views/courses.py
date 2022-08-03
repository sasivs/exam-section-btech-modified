from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from django.shortcuts import render
from MTco_ordinator.models import MTFacultyAssignment
from MThod.models import MTFaculty_user 
from MTsuperintendent.user_access_test import grades_threshold_access


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_access)
def courses_assigned(request):
    user = request.user
    faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    if not faculty:
        raise Http404('You are not assigned for any courses yet.')
    subjects = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    return render(request, 'MTfaculty/CoursesAssigned.html', {'subjects':subjects})
