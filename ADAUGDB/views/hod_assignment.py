from django.contrib.auth.decorators import login_required, user_passes_test
from ADAUGDB.user_access_test import is_Superintendent, hod_assignment_status_access
from django.shortcuts import render
from django.utils import timezone
from ADAUGDB.models import BTHOD
from ADAUGDB.forms import HODAssignmentForm

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def hod_assignment(request):
    if request.method == 'POST':
        form = HODAssignmentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('dept') and form.cleaned_data.get('hod') and form.cleaned_data.get('user') and 'submit-form' in request.POST.keys():
                initial_hod = BTHOD.objects.filter(RevokeDate__isnull=True, Dept=form.cleaned_data.get('dept')).first()
                if initial_hod:
                    if (initial_hod.Faculty.id != int(form.cleaned_data.get('hod'))) or (initial_hod.User.id != int(form.cleaned_data.get('user'))):
                        initial_hod.RevokeDate = timezone.now()
                        initial_hod.save()
                        new_hod = BTHOD(Faculty_id=form.cleaned_data.get('hod'), User_id=form.cleaned_data.get('user'), Dept=form.cleaned_data.get('dept'))
                        new_hod.save()
                        msg = 'Hod assignment is done successfully'
                    else:
                        msg = 'No change made in hod assignment'
                else:
                    new_hod = BTHOD(Faculty_id=form.cleaned_data.get('hod'), User_id=form.cleaned_data.get('user'), Dept=form.cleaned_data.get('dept'))
                    new_hod.save()
                    msg = 'Hod assignment is done successfully'
                return render(request, 'ADAUGDB/HodAssignment.html', {'form':form, 'msg':msg})
            else:
                if 'dept' in request.POST.keys():
                    initial_hod = BTHOD.objects.filter(Dept=request.POST.get('dept'), RevokeDate__isnull=True).first()
                    if initial_hod:
                        return render(request, 'ADAUGDB/HodAssignment.html', {'form':form, 'initial_hod':initial_hod.Faculty.id, 'initial_user':initial_hod.User.id})
    else:
        form = HODAssignmentForm()
    return render(request, 'ADAUGDB/HodAssignment.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(hod_assignment_status_access)
def hod_assignment_status(request):
    hods = BTHOD.objects.all()
    return render(request, 'ADAUGDB/HodAssignmentStatus.html', {'hod':hods})
