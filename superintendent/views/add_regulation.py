from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from SupExamDBRegistrations.views.home import is_Superintendent
from superintendent.models import Regulation
from superintendent.forms import AddRegulationForm

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
                msg = 'Regulation Added Successfully.'
                return render(request, 'superintendent/AddRegulation.html', {'form':form, 'msg':msg})
    else:
        form = AddRegulationForm()
    return render(request, 'superintendent/AddRegulation.html', {'form':form})