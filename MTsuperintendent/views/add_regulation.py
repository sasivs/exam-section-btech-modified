from django.shortcuts import render
from MTsuperintendent.user_access_test import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from import_export.formats.base_formats import XLSX
from MTsuperintendent.forms import AddRegulationForm
from MTsuperintendent.models import MTRegulation



@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def addRegulation(request):
    if request.method == 'POST':
        form = AddRegulationForm(request.POST)
        if(form.is_valid()):
            admYear = form.cleaned_data['admYear']
            ayear = form.cleaned_data['aYear']
            myear = form.cleaned_data['mYear']
            regulation = int(form.cleaned_data['regulation'])
        
            if(( (form.cleaned_data['admYear']!=0) and (form.cleaned_data['aYear']!=0) and (form.cleaned_data['mYear']!=0))):
                r = MTRegulation(AdmissionYear=admYear, AYear=ayear, MYear=myear, Regulation=regulation)
                r.save()
                msg = 'Regulation Added Successfully.'
                return render(request, 'superintendent/AddRegulation.html', {'form':form, 'msg':msg})
    else:
        form = AddRegulationForm()
    return render(request, 'superintendent/AddRegulation.html', {'form':form})