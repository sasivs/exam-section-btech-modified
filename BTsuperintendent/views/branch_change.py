
from django.contrib.auth.decorators import login_required, user_passes_test 
from BTsuperintendent.user_access_test import is_Superintendent
from django.shortcuts import render
from BTsuperintendent.forms import  BranchChangeForm, BranchChangeStausForm
from BTsuperintendent.models import BTBranchChanges
from BTExamStaffDB.models import BTStudentInfo


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
            row = BTStudentInfo.objects.filter(RegNo=regno).values()
            rollno = row[0]['RollNo']
            name = row[0]['Name']
            if currentDept != newDept:
                newRow = BTBranchChanges(RegNo=regno, RollNo=rollno, CurrentDept=currentDept, NewDept=newDept, AYear=ayear)
                newRow.save()
                BTStudentInfo.objects.filter(RegNo=regno).update(Dept=newDept)
                print(newRow)
                context['regno']=regno
                context['Name'] = name
                context['dept'] = newDept
                return render(request,'BTsuperindent/BTBranchChangeSuccess.html',context )
        else:
            print("form is not valid")
    else:
        form = BranchChangeForm()
    context['form']= form   
    return render(request,'BTsuperindent/BTBranchChange.html', context)

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
            results = BTBranchChanges.objects.filter(AYear=ayear).values()
            context['ayear'] = ayear
            context['rows'] = results
            return render(request, 'BTsuperindent/BTBranchChangeStatus.html', context)
        else:
            print('form validation failed')        
    else:
        form = BranchChangeStausForm()
    context['form'] = form
    return render(request, 'BTsuperindent/BTBranchChangeStatus.html', context)