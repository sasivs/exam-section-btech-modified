from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import is_Associate_Dean_Academics
from BTco_ordinator.forms import OpenElectiveRegistrationsForm
from BTco_ordinator.models import BTStudentRegistrations, BTStudentRegistrations_Staging,BTRollLists_Staging,BTRollLists
from ADAUGDB.forms import OpenElectiveRegistrationsFinalizeForm
from ADAUGDB.models import BTOpenElectiveRollLists
from ADAUGDB.models import BTRegistrationStatus
from import_export.formats.base_formats import XLSX
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def open_elective_regs(request):
    if(request.method == "POST"):
        form = OpenElectiveRegistrationsForm(request.POST)
        if request.POST.get('Submit'):
            if form.is_valid():
                rom2int = {'I':1,'II':2,'III':3,'IV':4}
                subid = form.cleaned_data.get('sub').split(',')
                regid = form.cleaned_data.get('regID')
                strs = regid.split(':')
                ayear = int(strs[2])
                asem = int(strs[3])
                byear = rom2int[strs[0]]
                bsem = rom2int[strs[1]]
                regulation = float(strs[4])
                mode = strs[5]
                
                rolls = BTOpenElectiveRollLists.objects.filter(subject_id__in=subid,RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode).order_by('student__student__RegNo')

                for roll in rolls:
                    if mode == 'R' or mode == 'D':
                        if not BTStudentRegistrations_Staging.objects.filter(student=roll.student, RegEventId_id=roll.RegEventId_id, Mode=1,sub_id_id=roll.subject_id).exists():
                            reg = BTStudentRegistrations_Staging(student=roll.student, RegEventId_id=roll.RegEventId_id, Mode=1,sub_id_id=roll.subject_id)
                            reg.save()
                return render(request, 'ADAUGDB/OecRegistrationsSuccess.html')
    else:
        form = OpenElectiveRegistrationsForm()
    return render(request, 'ADAUGDB/OpenElectiveRegistrations.html',{'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def open_elective_regs_finalize(request):
    if request.method == 'POST':
        form = OpenElectiveRegistrationsFinalizeForm(request.POST)
        if form.is_valid():
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            regid = form.cleaned_data.get('redID')
            strs = regid.split(':')
            ayear = int(strs[2])
            asem = int(strs[3])
            byear = rom2int[strs[0]]
            bsem = rom2int[strs[1]]
            regulation = float(strs[4])
            mode = strs[5]
            rolls = BTRollLists.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode)
            staging_regs = BTStudentRegistrations_Staging.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode,\
                sub_id__course__CourseStructure__Category__in=['OEC', 'OPC'])
            for reg in staging_regs:
                roll = rolls.filter(student=reg.student.student).first()
                final_reg = BTStudentRegistrations(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                final_reg.save()
            BTRegistrationStatus.objects.filter(AYear=ayear,BYear=byear,ASem=asem,BSem=bsem,Regulation=regulation,Mode=mode).update(OERegistrationStatus=0)
            msg = 'Open elective registrations are finalized.'
        return render(request, 'ADAUGDB/OpenElectiveRegistrationsFinalize.html', {'form':form, 'msg':msg})
    else:
        form = OpenElectiveRegistrationsFinalizeForm()
    return render(request, 'ADAUGDB/OpenElectiveRegistrationsFinalize.html', {'form':form})