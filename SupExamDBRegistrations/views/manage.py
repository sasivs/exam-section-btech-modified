from typing import Set
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse

from SupExamDBRegistrations.forms import DBYBSAYASSelectionForm
from SupExamDBRegistrations.models import ProgrammeModel, RegistrationStatus
from .home import is_Superintendent

# Create your views here.
@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def manage_registrations(request):
    if(request.method=='POST'):
        form = DBYBSAYASSelectionForm(request.POST)
        if(form.is_valid()):
            AYear = form.cleaned_data['aYearBox']
            ASem = form.cleaned_data['aSemBox']
            BYear = form.cleaned_data['bYearBox']
            BSem = form.cleaned_data['bSemBox']
            Dept = int(form.cleaned_data['deptBox'])
            Status = int(form.cleaned_data['statusBox'])
            Mode = form.cleaned_data['modeBox']
            prgs = ProgrammeModel.objects.filter(ProgrammeType='UG')
            romans = {1:'I',2:'II',3:'III',4:'IV'}
            if((BYear==1) and (Mode=='B')):
                regStatus = RegistrationStatus.objects.filter(AYear=AYear,ASem=ASem,BYear=BYear,BSem=BSem,Mode=Mode)
                if(len(regStatus)==0):
                    regStatusObj = RegistrationStatus(AYear=AYear,ASem=ASem,BYear=BYear,BSem=BSem,Dept=0, Status=Status,Mode=Mode)
                    regStatusObj.save()
                else:
                    regStatus.update(Status = Status)
                msg = 'Successfully updated registration status for AYear '+str(AYear)+'-'+str(AYear+1)+ ' ASem ' + str(ASem) + ' B.Tech. '+ str(BYear) + ' Sem '+ str(BSem) +  ' Mode:'+ Mode +' Status:'+str(Status)
            else:
                regStatus = RegistrationStatus.objects.filter(AYear=AYear,ASem=ASem,BYear=BYear,BSem=BSem,Dept=Dept,Mode=Mode)
                if(len(regStatus)==0):
                    regStatusObj = RegistrationStatus(AYear=AYear,ASem=ASem,BYear=BYear,BSem=BSem,Dept=Dept,Status=Status,Mode=Mode)
                    regStatusObj.save()
                else:
                    regStatus.update(Status = Status)
                prg = prgs.filter(Dept=Dept)
                prgName = ''
                if(len(prg)>0):
                    prgName = prg[0].Specialization
                msg = 'Successfully update registration status for AYear '+str(AYear)+'-'+str(AYear+1)+ ' ASem ' + str(ASem) + ' B.Tech. '+ romans[BYear] + ' Sem '+ romans[BSem] + ' Dept:' + prgName + ' Mode:'+ Mode +' Status:'+str(Status)
            return render(request, 'SupExamDBRegistrations/success_page.html', {'msg': msg})    
    else:
        form = DBYBSAYASSelectionForm()
    return render(request, 'SupExamDBRegistrations/BTRegistrationStatus.html',{'form':form})
