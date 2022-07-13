from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from superintendent.user_access_test import grades_finalize_access
from hod.forms import GradesFinalizeForm
from superintendent.models import RegistrationStatus, HOD
from faculty.models import StudentGrades_Staging, StudentGrades

import psycopg2


@login_required(login_url="/login/")
@user_passes_test(grades_finalize_access)
def grades_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'HOD' in groups:
        hod = HOD.objects.filter(User=user, RevokeDate__isnull=True)
        regIDs = RegistrationStatus.objects.filter(Status=1, GradeStatus=1, Dept=hod.Dept)
    if request.method == 'POST':
        form = GradesFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            if(form.cleaned_data['regID']!='--Choose Event--'):
                strs = form.cleaned_data['regID'].split(':')
                dept = deptDict[strs[0]]
                ayear = int(strs[3])
                asem = int(strs[4])
                byear = rom2int[strs[1]]
                bsem = rom2int[strs[2]]
                regulation = int(strs[5])
                mode = strs[6]
                currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
                grades = StudentGrades_Staging.objects.filter(RegEventId=currentRegEventId[0].id)
                for g in grades:
                    gr = StudentGrades(RegId=g.RegId, Regulation=g.Regulation, RegEventId=g.RegEventId, Grade=g.Grade, AttGrade=g.AttGrade)
                    gr.save()
                currentRegEventId[0].GradeStatus = 0
                currentRegEventId[0].save()
                RefreshMaterializedViews()
                return render(request, 'SupExamDBRegistrations/GradesFinalizeSuccess.html')
    else:
        form = GradesFinalizeForm(regIDs)
    return render(request, 'SupExamDBRegistrations/GradesFinalize.html', {'form':form})

def RefreshMaterializedViews():
    conn = psycopg2.connect(
    host="localhost",
    database="public",
    # name="public",
    user="postgres",
    password="postgresql")
    cursor = conn.cursor()

    try:
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"StudentGradePointsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"StudentBacklogsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"StudentMakeupBacklogsMV\" WITH DATA;")
    finally:
        cursor.close()
        conn.commit()