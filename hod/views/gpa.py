from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTco_ordinator.models import BTRollLists
from superintendent.user_access_test import gpa_staging_access
from superintendent.models import BTRegistrationStatus, BTHOD, BTStudentCGPAs_Staging, BTGradePoints
from hod.forms import GpaStagingForm

@login_required(login_url="/login/")
@user_passes_test(gpa_staging_access)
def gpa_staging(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIds = None
    if 'Superintendent' in groups:
        regIds = BTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIds = BTRegistrationStatus.objects.filter(Status=1, Dept__in=[hod.Dept, 9, 10])
    if request.method == 'POST':
        form = GpaStagingForm(regIds, request.POST)
        if form.is_valid():
            regEvent = regIds.filter(id=form.cleaned_data.get('regId')).first()
            rolls = BTRollLists.objects.filter(RegEventId=regEvent.id)
            ayasbybs = ((regEvent.AYear*10+regEvent.ASem)*10+regEvent.BYear)*10+regEvent.BSem
            gpa = BTStudentCGPAs_Staging.objects.filter(AYASBYBS_G=ayasbybs, RegNo__in=rolls.values_list('student__RegNo', flat=True)).order_by('RegNo')
            gpa_distribution = {}
            for gp in range(11):
                no_of_students = len(gpa.filter(CGPA__gte=gp, CGPA__lt=gp+1))
                if no_of_students != 0: gpa_distribution[gp]=no_of_students
            from json import dumps
            gpa_distribution = dumps(gpa_distribution)
            return render(request, 'hod/GPAStaging.html', {'form':form, 'gpa':gpa, 'gpa_data':gpa_distribution})
    else:
        form = GpaStagingForm(regIds)
    return render(request, 'hod/GPAStaging.html', {'form':form})
