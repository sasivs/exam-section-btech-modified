from django.http.response import HttpResponse, HttpResponseRedirect
from Registrations.models import CoordinatorMakeupRegNos, StudentMakeupBacklogs, StudentMakeupBacklogsVsRegistrations, StudentRegistrations,CurrentAcademicYear,CoordinatorInfo
from django.urls import reverse 
from Registrations.forms  import RegistrationsInsertionForm, SimpleForm, StudentIDForm, RegistrationForm
from django.shortcuts import render


def home(request):
    if(request.user.groups.filter(name='Superintendent').exists()):
        return HttpResponseRedirect(reverse('sindex'))
    elif(request.user.groups.filter(name='Coordinators').exists()):
        return HttpResponseRedirect(reverse('index'))
    elif(request.user.groups.filter(name='Coordinators1').exists()):
        return HttpResponseRedirect(reverse('cindex'))