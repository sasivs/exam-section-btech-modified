
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect

from superintendent.user_access_test import registration_access, pre_registrations_home_access, grades_home_access, faculty_home_access, \
    user_management_home_access, is_Superintendent, roll_list_status_access, marks_home_access, not_promoted_home_access

def logout_request(request):
    logout(request)
    return redirect("main:homepage")


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def registration_home(request):
    return render(request,'SupExamDBRegistrations/BTRegistrationHome.html')

@login_required(login_url="/login/")
@user_passes_test(grades_home_access)
def grades_home(request):
    return render(request, 'SupExamDBRegistrations/grades_home.html')

@login_required(login_url="/login/")
@user_passes_test(pre_registrations_home_access)
def pre_registrations_home(request):
    return render(request, 'SupExamDBRegistrations/preRegistrations_home.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def branch_change_home(request):
    return render(request, 'SupExamDBRegistrations/branchChange_home.html')

@login_required(login_url="/login/")
@user_passes_test(roll_list_status_access)
def rolllist_home(request):
    return render(request, 'SupExamDBRegistrations/rollList_home.html')

@login_required(login_url="/login/")
@user_passes_test(not_promoted_home_access)
def not_promoted_home(request):
    return render(request, 'SupExamDBRegistrations/not_promoted_home.html')


@login_required(login_url="/login/")
@user_passes_test(faculty_home_access)
def faculty_home(request):
    return render(request, 'SupExamDBRegistrations/faculty_home.html')

@login_required(login_url="/login/")
@user_passes_test(marks_home_access)
def marks_home(request):
    return render(request, 'SupExamDBRegistrations/marks_home.html')

@login_required(login_url="/login/")
@user_passes_test(user_management_home_access)
def userassignment_home(request):
    return render(request, 'SupExamDBRegistrations/userassignment_home.html')
