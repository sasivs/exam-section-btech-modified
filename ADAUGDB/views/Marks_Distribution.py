from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404 
from ADAUGDB.user_access_test import is_Superintendent, mark_distribution_status_access
from django.shortcuts import render
from ADAUGDB.forms import MarksDistributionForm
from ADAUGDB.models import BTMarksDistribution


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mark_distribution_add(request):
    if request.method == 'POST':
        form = MarksDistributionForm(request.POST)
        if(form.is_valid()):
            regulation = form.cleaned_data['Regulation']
            Distribution = form.cleaned_data['Distribution']
            marksDistribution = form.cleaned_data['DistributionName']
            promote_threshold = form.cleaned_data['PromoteThreshold']
            mark_distribution = BTMarksDistribution(Regulation=-regulation, Distribution=Distribution, DistributionNames=marksDistribution, PromoteThreshold=promote_threshold)
            mark_distribution.save()
            msg = 'Mark Distribution Added Successfully'
            return render(request, 'ADAUGDB/MarksDistribution.html', {'form':form, 'msg':msg})
    else:
        form = MarksDistributionForm()
    return render(request, 'ADAUGDB/MarksDistribution.html', {'form':form})

@login_required(login_url="/login/")
@user_passes_test(mark_distribution_status_access)
def mark_distribution_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    mark_distribution = BTMarksDistribution.objects.all()
    if request.method == 'POST':
        if not 'Superintendent' in groups:
            raise Http404('You are not authorized to view this page.')
        if request.POST.get('delete'):
            id = request.POST['delete']
            mark_distribution.filter(id=id).delete()
            mark_distribution = BTMarksDistribution.objects.all()
    return render(request, 'BTsuperintendent/MarkDistributionStatus.html', {'distributions':mark_distribution})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mark_distribution_update(request, pk):
    mark_distribution_obj = BTMarksDistribution.objects.get(id=pk)
    if request.method == 'POST':
        form = MarksDistributionForm(request.POST)
        if form.is_valid():
            regulation = form.cleaned_data['Regulation']
            Distribution = form.cleaned_data['Distribution']
            marksDistribution = form.cleaned_data['DistributionName']
            promote_threshold = form.cleaned_data['PromoteThreshold']
            mark_distribution_obj.Regulation = regulation
            mark_distribution_obj.Distribution = Distribution
            mark_distribution_obj.DistributionNames = marksDistribution
            mark_distribution_obj.PromoteThreshold = promote_threshold
            mark_distribution_obj.save()
            msg = 'Mark Distribution Updated Successfully'
            return render(request, 'ADAUGDB/MarksDistribution.html', {'form':form, 'msg':msg})
    else:
        initial_data = {'Regulation':mark_distribution_obj.Regulation, 'Distribution':mark_distribution_obj.Distribution, 'DistributionName':mark_distribution_obj.DistributionNames, \
            'PromoteThreshold':mark_distribution_obj.PromoteThreshold}
        form = MarksDistributionForm(initial=initial_data)
    return render(request, 'ADAUGDB/MarksDistribution.html', {'form':form})
