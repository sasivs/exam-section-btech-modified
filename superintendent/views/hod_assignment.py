from django.shortcuts import render
from django.utils import timezone
from django.contrib.auth.decorators import login_required, user_passes_test
from superintendent.user_access_test import is_Superintendent
from superintendent.models import HOD
from superintendent.forms import HODAssignmentForm

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def hod_assignment(request):
    if request.method == 'POST':
        form = HODAssignmentForm(request.POST)
        if form.is_valid():
            if form.cleaned_data.get('dept') and form.cleaned_data.get('hod') and form.cleaned_data.get('user') and form.cleaned_data.get('submit'):
                initial_hod = HOD.objects.filter(RevokeDate__isnull=True, Dept=form.cleaned_data.get('dept')).first()
                if initial_hod:
                    if (initial_hod.Faculty.id != form.cleaned_data.get('hod')) or (initial_hod.User.id != form.cleaned_data.get('user')):
                        initial_hod.RevokeDate = timezone.now()
                        initial_hod.save()
                        new_hod = HOD(Faculty_id=form.cleaned_data.get('hod'), User_id=form.cleaned_data.get('user'), Dept=form.cleaned_data.get('dept'))
                        new_hod.save()
                else:
                    new_hod = HOD(Faculty_id=form.cleaned_data.get('hod'), User_id=form.cleaned_data.get('user'), Dept=form.cleaned_data.get('dept'))
                    new_hod.save()
                msg = 'Hod assignment is done successfully'
                return render(request, 'superintendent/HodAssignment.html', {'form':form, 'msg':msg})
    else:
        form = HODAssignmentForm()
    return render(request, 'superintendent/HodAssignment.html', {'form':form})
