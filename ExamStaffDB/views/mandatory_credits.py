from django.contrib.auth.decorators import login_required, user_passes_test 
from superintendent.user_access_test import is_Superintendent
from django.shortcuts import render
from superintendent.forms import MandatoryCreditsForm
from superintendent.models import MandatoryCredits

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def mandatory_credits_upload(request):
    if(request.method == 'POST'):
        form = MandatoryCreditsForm(request.POST)
        # con = {key:request.POST[key] for key in request.POST.keys()}
        if form.is_valid():
            if(form.cleaned_data['Regulation'] != '-- Select Regulation --' and form.cleaned_data['BYear'] != '--Select BYear--' and \
                form.cleaned_data['Dept'] != '--Select Dept--' and form.cleaned_data['Credits'] != ''):
                regulation= form.cleaned_data['Regulation']
                byear =  form.cleaned_data['BYear']
                dept = form.cleaned_data['Dept']
                credits = int(form.cleaned_data['Credits'])
                mancred = MandatoryCredits.objects.filter(Regulation = regulation,BYear = byear, Dept= dept)
                
                if(len(mancred) != 0):
                    mancred.update(Credits = credits)
                else:
                    mancred = MandatoryCredits(Regulation = regulation,BYear = byear, Dept= dept,Credits=credits)
                    mancred.save()
                return render(request, 'ExamStaffDB/MandatoryCreditsUploadSuccess.html')
        else:
                form = MandatoryCreditsForm(request.POST)
                return render(request, 'ExamStaffDB/MandatoryCreditsUpload.html',{'form':form})
    else:
        form = MandatoryCreditsForm()
    return render(request, 'ExamStaffDB/MandatoryCreditsUpload.html',{'form':form})