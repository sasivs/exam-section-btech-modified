
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import DeptElectiveRegistrationsForm
from ADAUGDB.models import BTCycleCoordinator
from ADAUGDB.models import BTRegistrationStatus
from BTco_ordinator.models import BTSubjects, BTStudentRegistrations_Staging, BTRollLists_Staging
from import_export.formats.base_formats import XLSX
from BThod.models import BTCoordinator
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear,Mode__in=['R','B'])
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode__in=['R', 'B'])
    necessary_field_msg = False
    if(request.method == "POST"):
        form = DeptElectiveRegistrationsForm(regIDs,request.POST,request.FILES)
        if request.POST.get('Submit'):
            if form.is_valid():
                event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
                file = form.cleaned_data.get('file')
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                for i in range(len(dataset)):
                    regNo = int(dataset[i][0])
                    reg = BTStudentRegistrations_Staging(student=rolls.filter(student__RegNo=regNo).first(), RegEventId_id=event.id,Mode=1,\
                        sub_id_id=form.cleaned_data.get('subId'))
                    reg.save()
                return render(request, 'BTco_ordinator/Dec_Regs_success.html')
    else:
        form = DeptElectiveRegistrationsForm(regIDs)
    return render(request, 'BTco_ordinator/Dec_Registrations_upload.html',{'form':form,'msg':necessary_field_msg})
