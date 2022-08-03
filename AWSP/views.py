from django.shortcuts import render
from django.http.response import HttpResponseRedirect
from django.urls import reverse 


def home(request):
    if(request.user.groups.filter(name='Superintendent').exists()):
        return HttpResponseRedirect(reverse('sindex'))
    elif(request.user.groups.filter(name='Coordinators').exists()):
        return HttpResponseRedirect(reverse('index'))
    elif(request.user.groups.filter(name='Coordinators1').exists()):
        return HttpResponseRedirect(reverse('cindex'))
    elif(request.user.groups.filter(name='HOD').exists()):
        return HttpResponseRedirect(reverse('sindex'))
    elif(request.user.groups.filter(name='Faculty').exists()):
        return HttpResponseRedirect(reverse('sindex'))
    elif(request.user.groups.filter(name='Co-ordinator').exists()):
        return HttpResponseRedirect(reverse('sindex'))
    elif request.user.groups.filter(name='ExamStaff').exists():
        return HttpResponseRedirect(reverse('sindex'))
    elif request.user.groups.filter(name='Cycle-Co-ordinator').exists():
        return HttpResponseRedirect(reverse('sindex'))


# Create your views here.
def index(request):
    return render(request, 'BTsuperindent/index.html')