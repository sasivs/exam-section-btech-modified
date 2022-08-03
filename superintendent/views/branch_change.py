
from django.contrib.auth.decorators import login_required, user_passes_test 
from superintendent.user_access_test import is_Superintendent
from django.shortcuts import render
from superintendent.forms import  BranchChangeForm, BranchChangeStausForm
from superintendent.models import BranchChanges
from ExamStaffDB.models import StudentInfo


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def branch_change(request):
    context={}
    if(request.method=='POST'):
        form = BranchChangeForm(request.POST)
        if(form.is_valid()):
            regno = form.cleaned_data['RegNo']
            currentDept = form.cleaned_data['CurrentDept']
            newDept = form.cleaned_data['NewDept']
            ayear = form.cleaned_data['AYear']
            row = StudentInfo.objects.filter(RegNo=regno).values()
            rollno = row[0]['RollNo']
            name = row[0]['Name']
            if currentDept != newDept:
                newRow = BranchChanges(RegNo=regno, RollNo=rollno, CurrentDept=currentDept, NewDept=newDept, AYear=ayear)
                newRow.save()
                StudentInfo.objects.filter(RegNo=regno).update(Dept=newDept)
                print(newRow)
                context['regno']=regno
                context['Name'] = name
                context['dept'] = newDept
                return render(request,'superintendent/BTBranchChangeSuccess.html',context )
        else:
            print("form is not valid")
    else:
        form = BranchChangeForm()
    context['form']= form   
    return render(request,'superintendent/BTBranchChange.html', context)

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def branch_change_status(request):
    context={}
    if(request.method=='POST'):
        print(request.POST)
        print('post method')
        form = BranchChangeStausForm(request.POST)
        if(form.is_valid()):
            ayear = request.POST['AYear']
            print(ayear)
            results = BranchChanges.objects.filter(AYear=ayear).values()
            context['ayear'] = ayear
            context['rows'] = results
            return render(request, 'superintendent/BTBranchChangeStatus.html', context)
        else:
            print('form validation failed')        
    else:
        form = BranchChangeStausForm()
    context['form'] = form
    return render(request, 'superintendent/BTBranchChangeStatus.html', context)