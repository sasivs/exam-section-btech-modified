from django.contrib.auth.decorators import login_required, user_passes_test
from BTsuperintendent.user_access_test import is_Associate_Dean
from django.shortcuts import render
from ADUGDB.forms import CycleHandlerForm
from BTco_ordinator.models import BTNotPromoted 


@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean)
def cycle_handler(request):
    if request.method == 'POST':
        form = CycleHandlerForm(request.POST)
        if request.POST.get('Submit'):
            if form.is_valid():
                student = BTNotPromoted.objects.filter(id=form.cleaned_data.get('regno')).first().student
                student.Cycle = form.cleaned_data.get('cycle')
                student.save()
                msg = 'Student {}, cycle is updated to {}'.format(student.RegNo, 'Physics' if student.Cycle == 10 else 'Chemistry')
                return render(request, 'ADUGDB/RollListCycleHandler.html', {'form':form, 'msg':msg})
        elif request.POST.get('regno'):
            student = BTNotPromoted.objects.filter(RegNo=request.POST.get('regno')).first().student
            return render(request, 'ADUGDB/RollListCycleHandler.html', {'form':form, 'student':student})
    else:
        form = CycleHandlerForm()
    return render(request, 'ADUGDB/RollListCycleHandler.html', {'form':form})