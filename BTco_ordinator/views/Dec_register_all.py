from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import DeptElectiveRegsForm
from BTco_ordinator.models import BTRollLists_Staging, BTSubjects, BTStudentRegistrations_Staging
from ADAUGDB.models import BTCycleCoordinator
from ADAUGDB.models import BTRegistrationStatus
from BThod.models import BTCoordinator


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_all(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear,Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1,Mode='R')
    subjects=[]
    if(request.method == "POST"):
        form = DeptElectiveRegsForm(regIDs,subjects,request.POST)
        if request.POST.get('Submit'):
            if form.is_valid():
                event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()

                rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                for i in rolls:
                    reg = BTStudentRegistrations_Staging(student=i, RegEventId_id=event.id, Mode=1,sub_id_id=form.cleaned_data.get('subId'))
                    reg.save()
                rolls = rolls.values_list('student__RegNo', flat=True)
                BTStudentRegistrations_Staging.objects.filter(RegEventId=event).exclude(student__student__RegNo__in=rolls).delete()
                return render(request, 'BTco_ordinator/Dec_Regs_success.html')
        else:
            event = BTRegistrationStatus.objects.filter(id=request.POST.get('regID'))
            subjects = BTSubjects.objects.filter(RegEventId=event, course__CourseStructure__Category='DEC')
            subjects = [(sub.id,str(sub.course.SubCode)+" "+str(sub.course.SubName)) for sub in subjects]
            form = DeptElectiveRegsForm(regIDs,subjects,request.POST)
    else:
        form = DeptElectiveRegsForm(regIDs)
    return render(request, 'BTco_ordinator/Dec_register_all.html',{'form':form})
