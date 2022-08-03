from django.shortcuts import redirect, render
from django.http.response import HttpResponseRedirect
from django.urls import reverse 
from AWSP.forms import UG_PGSelectForm


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
    return render(request, 'BTsuperintendent/index.html')

def ug_pg(request):
    if request.method == 'POST':
        form = UG_PGSelectForm(request.POST)
        if form.is_valid():
            program = form.cleaned_data.get('program')
            if program == 'UG':
                return redirect('BThome')
            elif program == 'PG':
                return render('MThome')
    else:
        form = UG_PGSelectForm()
    return render(request, 'AWSP/UGPG.html', {'form':form})