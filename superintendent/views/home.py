
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect

from superintendent.user_access_test import registration_access, pre_registrations_home_access, grades_home_access, faculty_home_access, \
    user_management_home_access, is_Superintendent, roll_list_status_access, marks_home_access, not_promoted_home_access, subject_home_access,\
        registration_status_access

@login_required(login_url="/login/")
def sup_home(request):
    return render(request,'superintendent/suphome.html')

def logout_request(request):
    logout(request)
    return redirect("main:homepage")


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def registration_home(request):
    return render(request,'superintendent/BTRegistrationHome.html')

@login_required(login_url="/login/")
@user_passes_test(grades_home_access)
def grades_home(request):
    return render(request, 'superintendent/grades_home.html')

@login_required(login_url="/login/")
@user_passes_test(pre_registrations_home_access)
def pre_registrations_home(request):
    return render(request, 'superintendent/preRegistrations_home.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def branch_change_home(request):
    return render(request, 'superintendent/branchChange_home.html')

@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def rolllist_home(request):
    return render(request, 'superintendent/rollList_home.html')

@login_required(login_url="/login/")
@user_passes_test(not_promoted_home_access)
def not_promoted_home(request):
    return render(request, 'superintendent/not_promoted_home.html')


@login_required(login_url="/login/")
@user_passes_test(faculty_home_access)
def faculty_home(request):
    return render(request, 'superintendent/faculty_home.html')

@login_required(login_url="/login/")
@user_passes_test(marks_home_access)
def marks_home(request):
    return render(request, 'superintendent/marks_home.html')

@login_required(login_url="/login/")
@user_passes_test(user_management_home_access)
def userassignment_home(request):
    return render(request, 'superintendent/userassignment_home.html')


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def cancellation_home(request):
    return render(request, 'superintendent/registrationcancellation.html')


@login_required(login_url="/login/")
@user_passes_test(subject_home_access)
def subject_home(request):
    return render(request, 'superintendent/subjecthome.html')

@login_required(login_url="/login/")
@user_passes_test(registration_status_access)
def btech_registration_status_home(request):
    return render(request, 'superintendent/Status/registrationstatus.html')
