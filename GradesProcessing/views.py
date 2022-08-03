from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
# Create your views here.

def is_coordinator(user):
    if(user.groups.filter(name='Coordinators')):
        return user.groups.filter(name='Coordinators').exists()
    else:
        return user.groups.filter(name='Coordinators1').exists()


    
@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def gp_home(request):
    return render(request, 'GradesProcessing/gphome.html')

@login_required(login_url="/login/")
@user_passes_test(is_coordinator)
def gp_home1(request):
    return render(request, 'GradesProcessing/gphome1.html')


