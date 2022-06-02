from typing import Set
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse

from SupExamDBRegistrations.forms import DBYBSAYASSelectionForm
from SupExamDBRegistrations.models import ProgrammeModel, RegistrationStatus, RegularRegistrationSummary
from .home import is_Superintendent

# Create your views here.
@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def manage_registrations(request):
    if(request.method=='POST'):
        form = DBYBSAYASSelectionForm(request.POST)
        data = {key:request.POST[key] for key in request.POST.keys()}
        print(type(request.POST['regulation']))
        if request.POST['aYear']!='' and request.POST['bYear']!='' and request.POST['aYear']!='0' and \
            request.POST['bYear']!='0' and 'regulation' in request.POST.keys() and request.POST['regulation']!='0':
            AYear = request.POST['aYear']
        else:
            form = DBYBSAYASSelectionForm(data)
            return render(request, 'SupExamDBRegistrations/BTRegistrationStatus.html',{'form':form})

        if(request.POST['dept']!='0' and request.POST['bSem']!='0' and request.POST['aSem']!='0'):
            AYear = request.POST['aYear']
            ASem = request.POST['aSem']
            BYear = request.POST['bYear']
            BSem = request.POST['bSem']
            Dept = int(request.POST['dept'])
            Status = int(request.POST['status'])
            Mode = request.POST['mode']
            regulation = request.POST['regulation']
            rg_status = RegistrationStatus.objects.filter(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode)
            if(len(rg_status)==0):
                rg_status_obj = RegistrationStatus(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode, Status=Status)
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.BYear}:{rg_status_obj.BSem}:\
                    {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully registered({rg_status_obj.Status}) \
                        for {rg_status_obj.Mode} mode.'
                rg_status_obj.save()
                
            else:
                rg_status.update(Status=Status)
                rg_status_obj = RegistrationStatus.objects.get(AYear=AYear, ASem=ASem, BYear=BYear, BSem=BSem, Dept=Dept, Regulation=regulation, \
                Mode=Mode, Status=Status)
                msg = f'The event {rg_status_obj.AYear}:{rg_status_obj.ASem}:{rg_status_obj.BYear}:{rg_status_obj.BSem}:\
                    {rg_status_obj.Dept}:{rg_status_obj.Regulation} has been successfully updated({rg_status_obj.Status}) \
                        for {rg_status_obj.Mode} mode.'
            return render(request, 'SupExamDBRegistrations/success_page.html',{'msg':msg}) 
    else:
        form = DBYBSAYASSelectionForm()
    return render(request, 'SupExamDBRegistrations/BTRegistrationStatus.html',{'form':form})
