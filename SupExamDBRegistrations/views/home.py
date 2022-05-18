
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse
 

def is_Superintendent(user):
    return user.groups.filter(name='Superintendent').exists()

def logout_request(request):
    logout(request)
    return redirect("main:homepage")


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def registration_home(request):
    return render(request,'SupExamDBRegistrations/BTRegistrationHome.html')
