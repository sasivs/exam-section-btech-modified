from django.contrib.auth.decorators import login_required, user_passes_test 
from superintendent.user_access_test import is_Superintendent
from django.shortcuts import render
from superintendent.forms import MarksDistributionForm
from superintendent.models import MarksDistribution


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mark_distribution_add(request):
    if request.method == 'POST':
        form = MarksDistributionForm(request.POST)
        if(form.is_valid()):
            Distribution = form.cleaned_data['Distribution']
            MarksDistribution = form.cleaned_data['MarksDistribution']
            mark_distribution = MarksDistribution(Distribution=Distribution, MarksDistribution=MarksDistribution)
            mark_distribution.save()
            msg = 'Mark Distribution Added Successfully'
        return render(request, 'superintendent/MarksDistribution.html', {'form':form, 'msg':msg})
    else:
        form = MarksDistributionForm()
    return render(request, 'superintendent/MarksDistribution.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mark_distribution_status(request):
    mark_distribution = MarksDistribution.objects.all()
    if request.method == 'POST':
        if request.POST.get('delete'):
            id = request.POST['delete']
            mark_distribution.filter(id=id).delete()
            mark_distribution = MarksDistribution.objects.all()

    return render(request, 'superindent/MarkDistributionStatus.html', {'distributions':mark_distribution})
