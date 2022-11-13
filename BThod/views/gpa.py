from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTco_ordinator.models import BTRollLists
from BTsuperintendent.user_access_test import gpa_staging_access
from ADAUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTHOD, BTStudentCGPAs_Staging
from BThod.forms import GpaStagingForm
import psycopg2

@login_required(login_url="/login/")
@user_passes_test(gpa_staging_access)
def gpa_staging(request):
    from AWSP.settings import DATABASES
    conn = psycopg2.connect(
    host="localhost",
    database=DATABASES['default']['NAME'],
    user="postgres",
    password=DATABASES['default']['PASSWORD'])
    cursor = conn.cursor()

    try:
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentGradePointsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentGradePoints_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentExamEventsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentExamEvents_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentPresentPastResults_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentPresentPastResultsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentSGPAs_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentSGPAsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentCGPAs_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentCGPAsMV\" WITH DATA;")
        
    finally:
        cursor.close()
        conn.commit()
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIds = None
    if 'Superintendent' in groups or 'Associate-Dean' in groups:
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
            return render(request, 'BThod/GPAStaging.html', {'form':form, 'gpa':gpa, 'gpa_data':gpa_distribution})
    else:
        form = GpaStagingForm(regIds)
    return render(request, 'BThod/GPAStaging.html', {'form':form})
