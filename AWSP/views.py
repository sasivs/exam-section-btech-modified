from django.http import Http404
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required 
from django.urls import reverse 
from django.http.response import HttpResponseRedirect
from AWSP.forms import UG_PGSelectForm
from BThod.models import BTFaculty_user, BTCoordinator
from MThod.models import MTFaculty_user, MTCoordinator



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

@login_required(login_url="/login/")
def ug_pg(request):
    if request.method == 'POST':
        form = UG_PGSelectForm(request.POST)
        if form.is_valid():
            program = form.cleaned_data.get('program')
            if program == 'UG':
                return redirect('BThome')
            elif program == 'PG':
                return redirect('MThome')
    else:
        form = UG_PGSelectForm()
        groups = request.user.groups.all().values_list('name', flat=True)
        if 'Cycle-Co-ordinator' in groups:
            return redirect('BThome')
        if 'Faculty' in groups:
            btech = BTFaculty_user.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
            mtech = MTFaculty_user.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
            if btech and not mtech:
                return redirect('BThome')
            if mtech and not btech:
                return redirect('MThome')
        if 'Co-ordinator' in groups:
            btech = BTCoordinator.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
            mtech = MTCoordinator.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
            if btech and not mtech:
                return redirect('BThome')
            if mtech and not btech:
                return redirect('MThome')
    return render(request, 'BTsuperintendent/UGPG.html', {'form':form})

@login_required(login_url="/login/")
def switch_programme(request, pr_code):
    groups = request.user.groups.all().values_list('name', flat=True)
    if 'Faculty' in groups:
        btech = BTFaculty_user.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
        mtech = MTFaculty_user.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
        if pr_code == 'BT' and mtech:
            return redirect('MThome')
        elif pr_code == 'BT' and not mtech:
            return redirect(request.META.get('HTTP_REFERER'))
        elif pr_code == 'MT' and btech:
            return redirect('BThome')
        elif pr_code == 'MT' and not btech:
            return redirect(request.META.get('HTTP_REFERER'))
        else: return Http404('Error, Invalid arguments.')
    elif 'Co-ordinator' in groups:
        btech = BTCoordinator.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
        mtech = MTCoordinator.objects.filter(User=request.user, RevokeDate__isnull=True).exists()
        if pr_code == 'BT' and mtech:
            return redirect('MThome')
        elif pr_code == 'BT' and not mtech:
            return redirect(request.META.get('HTTP_REFERER'))
        elif pr_code == 'MT' and btech:
            return redirect('BThome')
        elif pr_code == 'MT' and not btech:
            return redirect(request.META.get('HTTP_REFERER'))
        else: return Http404('Error, Invalid arguments.')
    elif 'Cycle-Co-ordinator' in groups:
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        if pr_code == 'BT': return redirect('MThome')
        elif pr_code == 'MT': return redirect('BThome')
        else: return Http404('Error, Invalid arguments.')

    