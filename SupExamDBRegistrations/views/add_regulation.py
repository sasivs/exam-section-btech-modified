from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render,redirect
from django.urls import reverse
from SupExamDBRegistrations.forms import BacklogRegistrationForm, RegistrationsEventForm, \
    SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, AddRegulationForm
from SupExamDBRegistrations.models import RegistrationStatus, StudentBacklogs, StudentInfo, StudentRegistrations,\
     Subjects, Subjects_Staging, Regulation
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from django.contrib import messages
from tablib import Dataset
from import_export.formats.base_formats import XLSX

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def addRegulation(request):
    if request.method == 'POST':
        form = AddRegulationForm(request.POST)
        if(form.is_valid()):
            admYear = form.cleaned_data['admYear']
            ayear = form.cleaned_data['aYear']
            byear = form.cleaned_data['bYear']
            regulation = int(form.cleaned_data['regulation'])
            if(( (form.cleaned_data['admYear']!=0) and (form.cleaned_data['aYear']!=0) and (form.cleaned_data['bYear']!=0))):
                r = Regulation(AdmissionYear=admYear, AYear=ayear, BYear=byear, Regulation=regulation)
                r.save()
                return HttpResponse("Saved Successfully")

            else:
                return HttpResponse("ERROR MESSAGE:All The Fields Are Required")
            # messages.success(request, f'Added Regulation: {r.Regulation} for AdmYear: {r.AdmissionYear}, \
            #     AYear: {r.AYear}, BYear: {r.BYear}')
            # return redirect('SupBTRegistrationHome')
            # return render(request, 'SupExamDBRegistrations/registra')
    else:
        form = AddRegulationForm()
    return render(request, 'SupExamDBRegistrations/addRegulation.html', {'form':form})