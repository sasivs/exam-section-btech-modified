from django.contrib.auth.decorators import login_required, user_passes_test
from BTco_ordinator.models import BTFacultyAssignment
from BTsuperintendent.user_access_test import is_Hod
from django.shortcuts import render
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTHOD
from BThod.forms import MarksFinalizeForm
from BTco_ordinator.models import BTStudentRegistrations
from BTfaculty.models import BTMarks_Staging, BTMarks, BTStudentGrades_Staging, BTStudentGrades


@login_required(login_url="/login/")
@user_passes_test(is_Hod)
def marks_finalize(request):

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__MarksStatus=1, Subject__OfferedBy=hod.Dept)
        regIDs = BTRegistrationStatus.objects.filter(id__in=subjects.values_list('RegEventId_id', flat=True))
    msg = ''
    if request.method == 'POST':
        form = MarksFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            regEvent = form.cleaned_data.get('regEvent')
            marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id__in=subjects.values_list('Subject_id', flat=True)).order_by('Registration__RegNo')
            final_marks_objects = BTMarks.objects.filter(Registration_id__in=marks_objects.values_list('Registration_id', flat=True))
            for mark in marks_objects:
                final_mark = final_marks_objects.filter(Registration=mark.Registration).first()
                if final_mark:
                    final_mark.Marks = mark.Marks
                    final_mark.TotalMarks = mark.TotalMarks
                    final_mark.save()
            msg = 'Marks are finalized successfully.'
            # reg_status_obj = RegistrationStatus.objects.get(id=regEvent)
            # reg_status_obj.MarksStatus = 0
            # reg_status_obj.save()
    else:
        form = MarksFinalizeForm(regIDs)
    return render(request, 'BTfaculty/MarksFinalize.html', {'form':form, 'msg':msg})

def marks_grades_finalize(**kwargs):
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    dept = kwargs.get('Dept')
    byear = kwargs.get('BYear')
    if not kwargs.get('Dept') and not kwargs.get('BYear'):
        dept = [1,2,3,4,5,6,7,8,9,10]
        byear = [1,2,3,4]
    elif not kwargs.get('Dept'):
        dept = []
        if 2 in kwargs.get('BYear') or 3 in kwargs.get('BYear') or 4 in kwargs.get('BYear'):
            dept.extend([1,2,3,4,5,6,7,8])
        if 1 in kwargs.get('BYear'):
            dept.extend([9,10])
    elif not kwargs.get('BYear'):
        byear = [1,2,3,4]
    asem = kwargs.get('ASem')
    bsem = kwargs.get('BSem')
    if not kwargs.get('ASem'):
        asem = [1,2,3]
    if not kwargs.get('BSem'):
        bsem = [1,2]
    regEvents = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), Regulation=kwargs.get('Regulation'), Mode=kwargs.get('Mode'), BYear__in=byear, BSem__in=bsem, \
        ASem__in=asem, Dept__in=dept)
    marks_rows = BTMarks_Staging.objects.filter(Registration__RegEventId_id__in=regEvents.values_list('id', flat=True))
    for mark in marks_rows:
        print(mark.__dict__)
        BTMarks.objects.filter(Registration_id=mark.Registration.id).update(Marks=mark.Marks, TotalMarks=mark.TotalMarks)
    grades_rows = BTStudentGrades_Staging.objects.filter(RegEventId__in=regEvents.values_list('id', flat=True))
    for grade in grades_rows:
        print(grade.__dict__)
        grade_fin = BTStudentGrades(RegId=grade.RegId, RegEventId=grade.RegEventId, Grade=grade.Grade, AttGrade=grade.AttGrade, Regulation=grade.Regulation)
        grade_fin.save
    # for event in regEvents:
    #     print(event.__dict__)
    return "Completed!!!"

def finalize_marks(**kwargs):
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
        return "No Events!!!!"
    for event in regEvents:
        registrations = BTStudentRegistrations.objects.filter(RegEventId_id=event.id)
        marks_objs = BTMarks_Staging.objects.filter(Registration_id__in=registrations.values_list('id', flat=True))
        for mark in marks_objs:
            fmark = BTMarks.objects.filter(Registration=mark.Registration).update(Marks=mark.Marks, TotalMarks=mark.TotalMarks)
    return "Completed!!"