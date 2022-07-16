from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from co_ordinator.models import FacultyAssignment, StudentRegistrations, Subjects
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
        hod = HOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, Subject__OfferedBy=hod.Dept).distinct('Subject')
    if request.method == 'POST':
        form = GradesFinalizeForm(subjects, request.POST)
        if form.is_valid():
            if form.cleaned_data['subject']:
                subject = form.cleaned_data['subject'].split(':')[0]
                regEvent = form.cleaned_data['subject'].split(':')[1]
                student_registrations = StudentRegistrations.objects.filter(RegEventId=regEvent, sub_id=subject)
                grades = StudentGrades_Staging.objects.filter(RegEventId=regEvent, RegId__in=student_registrations.values_list('id', flat=True))
                for g in grades:
                    gr = StudentGrades(RegId=g.RegId, Regulation=g.Regulation, RegEventId=g.RegEventId, Grade=g.Grade, AttGrade=g.AttGrade)
                    gr.save()
                RefreshMaterializedViews()
                msg = 'Grades have been finalized.'
                return render(request, 'hod/GradesFinalize.html', {'form':form, 'msg':msg})
    else:
        form = GradesFinalizeForm(subjects)
    return render(request, 'hod/GradesFinalize.html', {'form':form})

def RefreshMaterializedViews():
    conn = psycopg2.connect(
    host="localhost",
    database="public",
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