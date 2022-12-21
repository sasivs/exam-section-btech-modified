
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import DeptElectiveRegistrationsForm
from ADAUGDB.models import BTCycleCoordinator
from ADAUGDB.models import BTRegistrationStatus
from BTco_ordinator.models import BTSubjects, BTStudentRegistrations_Staging, BTRollLists_Staging, BTStudentBacklogs, BTDroppedRegularCourses
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
        subjects = BTSubjects.objects.filter(course__CourseStructure__Category__in=['DEC'], RegEventId__Status=1, RegEventId__RegistrationStatus=1, RegEventId__Dept=coordinator.Dept, \
            RegEventId__BYear=coordinator.BYear)
        backlogs = BTStudentBacklogs.objects.filter(Category__in=['DEC'], Dept=coordinator.Dept, BYear=coordinator.BYear)
        dropped = BTDroppedRegularCourses.objects.filter(subject__course__CourseStructure__Category__in=['DEC'], RegEventId__BYear=coordinator.BYear, RegEventId__Dept=coordinator.Dept)
        regular_regIds = BTRegistrationStatus.objects.filter(id__in=subjects.values_list('RegEventId_id', flat=True))
        backlog_regIds = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='B', \
            BSem__in=backlogs.values_list('BSem', flat=True))
        dropped_regIds = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='D', \
            BSem__in=dropped.values_list('RegEventId__BSem', flat=True))
        regIDs = regular_regIds | dropped_regIds | backlog_regIds
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTSubjects.objects.filter(course__CourseStructure__Category__in=['DEC'], RegEventId__Status=1, RegEventId__RegistrationStatus=1, RegEventId__Dept=cycle_cord.Cycle, \
            RegEventId__BYear=1)
        backlogs = BTStudentBacklogs.objects.filter(Category__in=['DEC'], Dept=cycle_cord.Cycle, BYear=1)
        dropped = BTDroppedRegularCourses.objects.filter(subject__course__CourseStructure__Category__in=['DEC'], RegEventId__BYear=1, RegEventId__Dept=cycle_cord.Cycle)
        regular_regIds = BTRegistrationStatus.objects.filter(id__in=subjects.values_list('RegEventId_id', flat=True))
        backlog_regIds = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='B', \
            BSem__in=backlogs.values_list('BSem', flat=True))
        dropped_regIds = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='D', \
            BSem__in=dropped.values_list('RegEventId__BSem', flat=True))
        regIDs = regular_regIds | dropped_regIds | backlog_regIds
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
                    mode = 1
                    if event.Mode == 'B':
                        mode = int(dataset[i][1])
                    if not BTStudentRegistrations_Staging.objects.filter(student=rolls.filter(student__RegNo=regNo).first(), RegEventId_id=event.id,Mode=mode,\
                        sub_id_id=form.cleaned_data.get('subId')).exists():
                        reg = BTStudentRegistrations_Staging(student=rolls.filter(student__RegNo=regNo).first(), RegEventId_id=event.id,Mode=mode,\
                            sub_id_id=form.cleaned_data.get('subId'))
                        reg.save()
                return render(request, 'BTco_ordinator/Dec_Regs_success.html')
    else:
        form = DeptElectiveRegistrationsForm(regIDs)
    return render(request, 'BTco_ordinator/Dec_Registrations_upload.html',{'form':form,'msg':necessary_field_msg})
