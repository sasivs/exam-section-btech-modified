from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTco_ordinator.models import BTFacultyAssignment, BTStudentRegistrations, BTSubjects
from BTsuperintendent.user_access_test import grades_finalize_access
from BThod.forms import GradesFinalizeForm
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTHOD
from BTfaculty.models import BTStudentGrades_Staging, BTStudentGrades

import psycopg2


@login_required(login_url="/login/")
@user_passes_test(grades_finalize_access)
def grades_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, Subject__OfferedBy=hod.Dept)
        regIDs = BTRegistrationStatus.objects.filter(id__in=subjects.values_list('RegEventId_id', flat=True))
    if request.method == 'POST':
        form = GradesFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            regEvent = form.cleaned_data['regEvent']
            student_registrations = BTStudentRegistrations.objects.filter(RegEventId=regEvent, sub_id__in=subjects.values_list('Subject_id', flat=True))
            grades = BTStudentGrades_Staging.objects.filter(RegEventId=regEvent, RegId__in=student_registrations.values_list('id', flat=True))
            if BTStudentGrades.objects.filter(RegEventId=regEvent, RegId__in=student_registrations.values_list('id', flat=True)).exists():
                msg = 'Grades Have already been finalized.'
            else:
                for g in grades:
                    gr = BTStudentGrades(RegId=g.RegId, Regulation=g.Regulation, RegEventId=g.RegEventId, Grade=g.Grade, AttGrade=g.AttGrade)
                    gr.save()
                RefreshMaterializedViews()
                msg = 'Grades have been finalized.'
            # reg_status_obj = RegistrationStatus.objects.get(id=regEvent)
            # reg_status_obj.GradeStatus = 0
            # reg_status_obj.save()
            return render(request, 'BThod/GradesFinalize.html', {'form':form, 'msg':msg})
    else:
        form = GradesFinalizeForm(regIDs)
    return render(request, 'BThod/GradesFinalize.html', {'form':form})

def RefreshMaterializedViews():
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
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentBacklogsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentMakeupBacklogsMV\" WITH DATA;")
    finally:
        cursor.close()
        conn.commit()

def finalize_grades(**kwargs):
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
        return "No Events!!!!"
    for event in regEvents:
        registrations = BTStudentRegistrations.objects.filter(RegEventId_id=event.id)
        grades_objs = BTStudentGrades_Staging.objects.filter(RegId__in=registrations.values_list('id', flat=True))
        for grade in grades_objs:
            fgrade = BTStudentGrades(RegId=grade.RegId, RegEventId=grade.RegEventId.id, Regulation=grade.Regulation, Grade=grade.Grade, AttGrade=grade.AttGrade)
            fgrade.save()
    return "Completed!!"