from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import DeptElectiveRegsForm
from BTco_ordinator.models import BTRollLists_Staging, BTSubjects, BTStudentRegistrations_Staging, BTStudentBacklogs, BTDroppedRegularCourses
from ADAUGDB.models import BTCycleCoordinator
from ADAUGDB.models import BTRegistrationStatus
from BThod.models import BTCoordinator
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_all(request):
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
        regIDs = regular_regIds.union(dropped_regIds.union(backlog_regIds))
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
        regIDs = regular_regIds.union(dropped_regIds.union(backlog_regIds))
    subjects=[]
    if(request.method == "POST"):
        form = DeptElectiveRegsForm(regIDs,subjects,request.POST)
        if request.POST.get('Submit'):
            if form.is_valid():
                event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()

                rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                for i in rolls:
                    if not BTStudentRegistrations_Staging.objects.filter(student=i, RegEventId_id=event.id, Mode=1,sub_id_id=form.cleaned_data.get('subId')).exists():
                        reg = BTStudentRegistrations_Staging(student=i, RegEventId_id=event.id, Mode=1,sub_id_id=form.cleaned_data.get('subId'))
                        reg.save()
                rolls = rolls.values_list('student__RegNo', flat=True)
                BTStudentRegistrations_Staging.objects.filter(RegEventId=event).exclude(student__student__RegNo__in=rolls).delete()
                return render(request, 'BTco_ordinator/Dec_Regs_success.html')
        else:
            event = BTRegistrationStatus.objects.filter(id=request.POST.get('regID')).first()
            if event.Mode == 'R':
                subjects = BTSubjects.objects.filter(RegEventId=event, course__CourseStructure__Category='DEC')
            elif event.Mode == 'B':
                subjects = BTSubjects.objects.filter(course__CourseStructure__Category__in=['DEC'], RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                # backlog_subjects = BTStudentBacklogs.objects.filter(BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, \
                #     Regulation=event.Regulation, Category__in=['DEC']).exclude(AYASBYBS__startswith__lt=event.AYear).values_list('sub_id',flat=True)
                # subjects = BTSubjects.objects.filter(id__in=backlog_subjects)
            elif event.Mode == 'D':
                subjects = BTSubjects.objects.filter(subject__course__CourseStructure__Category__in=['DEC'], RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                    RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                # dropped_subjects = BTDroppedRegularCourses.objects.filter(subject__course__CourseStructure__Category__in=['DEC'], \
                #     RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Dept=event.Dept, RegEventId__Regulation=event.Regulation).\
                #         values_list('subject_id', flat=True)
                # subjects = BTSubjects.objects.filter(id__in=dropped_subjects)
            subjects = [(sub.id,str(sub.course.SubCode)+" "+str(sub.course.SubName)) for sub in subjects]
            form = DeptElectiveRegsForm(regIDs,subjects,request.POST)
    else:
        form = DeptElectiveRegsForm(regIDs)
    return render(request, 'BTco_ordinator/Dec_register_all.html',{'form':form})
