from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTco_ordinator.models import MTRollLists
from MTsuperintendent.user_access_test import gpa_staging_access
from MTsuperintendent.models import MTRegistrationStatus, MTHOD, MTStudentCGPAs_Staging, MTGradePoints
from MThod.forms import GpaStagingForm

@login_required(login_url="/login/")
@user_passes_test(gpa_staging_access)
def gpa_staging(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIds = None
    if 'Superintendent' in groups:
        regIds = MTRegistrationStatus.objects.filter(Status=1)
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIds = MTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept)
    if request.method == 'POST':
        form = GpaStagingForm(regIds, request.POST)
        if form.is_valid():
            regEvent = regIds.filter(id=form.cleaned_data.get('regId')).first()
            rolls = MTRollLists.objects.filter(RegEventId=regEvent.id)
            ayasbybs = ((regEvent.AYear*10+regEvent.ASem)*10+regEvent.MYear)*10+regEvent.MSem
            gpa = MTStudentCGPAs_Staging.objects.filter(AYASMYMS_G=ayasbybs, RegNo__in=rolls.values_list('student__RegNo', flat=True)).order_by('RegNo')
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
