from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import is_Associate_Dean_Academics
from ADAUGDB.models import BTRegulation
from ADAUGDB.forms import AddRegulationForm

@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def addRegulation(request):
    if request.method == 'POST':
        form = AddRegulationForm(request.POST)
        if(form.is_valid()):
            admYear = form.cleaned_data['admYear']
            ayear = form.cleaned_data['aYear']
            byear = form.cleaned_data['bYear']
            regulation = int(form.cleaned_data['regulation'])
            if(( (form.cleaned_data['admYear']!=0) and (form.cleaned_data['aYear']!=0) and (form.cleaned_data['bYear']!=0))):
                r = BTRegulation(AdmissionYear=admYear, AYear=ayear, BYear=byear, Regulation=regulation)
                r.save()
                msg = 'Regulation Added Successfully.'
                return render(request, 'ADAUGDB/AddRegulation.html', {'form':form, 'msg':msg})
    else:
        form = AddRegulationForm()
    return render(request, 'ADAUGDB/AddRegulation.html', {'form':form})