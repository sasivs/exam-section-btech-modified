from django.contrib.auth.decorators import login_required, user_passes_test
from co_ordinator.models import BTFacultyAssignment
from superintendent.user_access_test import is_Hod
from django.shortcuts import render
from superintendent.models import BTRegistrationStatus, BTHOD
from hod.forms import MarksFinalizeForm
from faculty.models import BTMarks_Staging, BTMarks


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
    return render(request, 'faculty/MarksFinalize.html', {'form':form, 'msg':msg})