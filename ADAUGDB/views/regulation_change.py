from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import is_Associate_Dean_Academics, regulation_change_status_access
from django.shortcuts import render
from ADAUGDB.forms import RegulationChangeForm, RegulationChangeStatusForm
from BTco_ordinator.models import BTNotPromoted, BTRegulationChange
from ADAUGDB.models import BTHOD, BTCycleCoordinator
from BThod.models import BTCoordinator
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def regulation_change(request):
    if request.method == 'POST':
        form  = RegulationChangeForm(request.POST)
        if request.POST.get('Submit'):
            if form.is_valid():
                student = BTNotPromoted.objects.filter(id=form.cleaned_data.get('regno')).first().student
                if not BTRegulationChange.objects.filter(RegEventId_id=form.cleaned_data.get('regid'),student=student).exists():
                    newRow = BTRegulationChange.objects.filter(RegEventId_id=form.cleaned_data.get('regid'), \
                        PreviiousRegulation=student.Regulation, PresentRegulation=form.cleaned_data.get('newRegulation'), student=student)
                    newRow.save()
                    msg = 'Regulation Change performed successfully.'
                else:
                    msg = 'Regulation change already performed for this candidate for this registration event.'
                return render(request, 'ADAUGDB/RegulationChange.html', {'form':form, 'msg':msg})
        elif request.POST.get('regno'):
            student = BTNotPromoted.objects.filter(RegNo=request.POST.get('regno')).first().student
            return render(request, 'ADAUGDB/RegulationChange.html', {'form':form, 'student':student})
    else:
        form = RegulationChangeForm()
    return render(request, 'ADAUGDB/RegulationChange.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(regulation_change_status_access)
def regulation_change_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        regulation_change_objs = BTRegulationChange.objects.all()
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regulation_change_objs = BTRegulationChange.objects.filter(RegEventId__Dept=hod.Dept)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regulation_change_objs = BTRegulationChange.objects.filter(RegEventId__Dept=co_ordinator.Dept, RegEventId__BYear=co_ordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        co_ordinator = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regulation_change_objs = BTRegulationChange.objects.filter(RegEventId__Dept=co_ordinator.Cycle)
    if request.method == 'POST':
        form = RegulationChangeStatusForm(regulation_change_objs, request.POST)
        if form.is_valid():
            return render(request, 'ADAUGDB/RegulationChangeStatus.html', {'form':form, 'objects':regulation_change_objs})

    else:
        form = RegulationChangeStatusForm(regulation_change_objs)
    return render(request, 'ADAUGDB/RegulationChange.html', {'form':form})