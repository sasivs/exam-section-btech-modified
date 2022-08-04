from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTco_ordinator.models import MTFacultyAssignment, MTStudentRegistrations, MTSubjects
from MTsuperintendent.user_access_test import grades_finalize_access
from MThod.forms import GradesFinalizeForm
from MTsuperintendent.models import MTRegistrationStatus, MTHOD
from MTfaculty.models import MTStudentGrades_Staging, MTStudentGrades

import psycopg2


@login_required(login_url="/login/")
@user_passes_test(grades_finalize_access)
def grades_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, Subject__OfferedBy=hod.Dept)
        regIDs = MTRegistrationStatus.objects.filter(id__in=subjects.values_list('RegEventId_id', flat=True))
    if request.method == 'POST':
       form = GradesFinalizeForm(regIDs, request.POST)
       if form.is_valid():
            regEvent = form.cleaned_data['regEvent']
            student_registrations = MTStudentRegistrations.objects.filter(RegEventId=regEvent, sub_id__in=subjects.values_list('Subject_id', flat=True))
            grades = MTStudentGrades_Staging.objects.filter(RegEventId=regEvent, RegId__in=student_registrations.values_list('id', flat=True))
            if MTStudentGrades.objects.filter(RegEventId=regEvent, RegId__in=student_registrations.values_list('id', flat=True)).exists():
                msg = 'Grades Have already been finalized.'
            else:
                for g in grades:
                    gr = MTStudentGrades(RegId=g.RegId, Regulation=g.Regulation, RegEventId=g.RegEventId, Grade=g.Grade, AttGrade=g.AttGrade)
                    gr.save()
                RefreshMaterializedViews()
                msg = 'Grades have been finalized.'
                # reg_status_obj = MTRegistrationStatus.objects.get(id=regEvent)
                # reg_status_obj.GradeStatus = 0
                # reg_status_obj.save()
            return render(request, 'MThod/GradesFinalize.html', {'form':form, 'msg':msg})

    else:
        form = GradesFinalizeForm(regIDs)
    return render(request, 'SupExamDBRegistrations/GradesFinalize.html', {'form':form})


def RefreshMaterializedViews():
    conn = psycopg2.connect(
    host="localhost",
    database="exam_mtech",
    # name="public",
    user="postgres",
    password="postgresql")
    cursor = conn.cursor()

    try:
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"MTStudentGradePointsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"MTStudentGradePoints_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"MTStudentBacklogsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"MTStudentMakeupBacklogsMV\" WITH DATA;")
    finally:
        cursor.close()
        conn.commit()

