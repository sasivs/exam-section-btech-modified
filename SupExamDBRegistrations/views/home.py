
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect

from superintendent.user_access_test import roll_list_access
 

def is_Superintendent(user):
    return user.groups.filter(name='Superintendent').exists()

def logout_request(request):
    logout(request)
    return redirect("main:homepage")


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def registration_home(request):
    return render(request,'SupExamDBRegistrations/BTRegistrationHome.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def grades_home(request):
    return render(request, 'SupExamDBRegistrations/grades_home.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def pre_registrations_home(request):
    return render(request, 'SupExamDBRegistrations/preRegistrations_home.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def branch_change_home(request):
    return render(request, 'SupExamDBRegistrations/branchChange_home.html')

@login_required(login_url="/login/")
@user_passes_test(roll_list_access)
def rolllist_home(request):
    return render(request, 'SupExamDBRegistrations/rollList_home.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def not_promoted_home(request):
    return render(request, 'SupExamDBRegistrations/not_promoted_home.html')


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def faculty_home(request):
    return render(request, 'SupExamDBRegistrations/faculty_home.html')

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def marks_home(request):
    return render(request, 'SupExamDBRegistrations/marks_home.html')
