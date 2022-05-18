
from unicodedata import name
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from SupExamDB.forms import DeptYearSelectionForm
from SupExamDB.models import ProgrammeModel
from SupExamDBRegistrations.forms import BacklogRegistrationForm, BranchChangeForm, BranchChangeStausForm
from SupExamDBRegistrations.models import BranchChanges, StudentBacklogs, StudentInfo, StudentRegistrations
from .home import is_Superintendent
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_backlog_registration(request):
    studentInfo = []
    if(request.method == 'POST'):
        print(request.POST)
        event = request.POST['RegEvent']
        eventDetails = event.split('-')
        depts = {"BTE":1,"CHE":2,"CE":3,"CSE":4,"EEE":5,"ECE":6,"ME":7,"MME":8,"Chemistry":9,"Physics":10}
        romans2int = {"I":1,"II":2,"III":3,"IV":4}
        dept = depts[eventDetails[0]]
        byear = romans2int[eventDetails[3]]
        ayear = int(eventDetails[1])
        asem = romans2int[eventDetails[2]]
        bsem = romans2int[eventDetails[4]]
        con = {key:request.POST[key] for key in request.POST.keys()} 
        if('RegNo' in request.POST.keys()):
            studentBacklogs = StudentBacklogs.objects.filter(RegNo=request.POST['RegNo']).filter(BYear = byear)
            studentRegistrations = StudentRegistrations.objects.filter(RegNo=request.POST['RegNo'],AYear=ayear,ASem=asem)
            Selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
            studentRegularRegistrations = studentRegistrations.filter(AYear= F('OfferedYear'))
            for row in studentBacklogs:
                print(row.SubCode)
                studentRegularRegistrations = studentRegularRegistrations.values()
                for entry in studentRegularRegistrations:
                    print(entry)
                    if row.SubCode == entry['SubCode']:
                        con[str('RadioMode'+row.SubCode)] = list(str(entry['Mode']))

        form = BacklogRegistrationForm(con)
        if not 'RegNo' in request.POST.keys():
            pass #return render(request, 'SupExamDBRegistrations/BTBacklogRegistration.html',{'form':form})
        elif not 'Submit' in request.POST.keys():
            regNo = request.POST['RegNo']
            event = (request.POST['RegEvent'])
            print(regNo, event)
            studentInfo = StudentInfo.objects.filter(RegNo=regNo)
            #return render(request, 'SupExamDBRegistrations/BTBacklogRegistration.html', {'form': form, 'Name':studentInfo[0].Name, 'RollNo':studentInfo[0].RollNo})
        elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
            print(form.cleaned_data['RegEvent'])
            print(form.cleaned_data['RegNo'])
            studyModeCredits = 0
            examModeCredits = 0
            for sub in form.myFields:
                print(form.cleaned_data['RadioMode'+sub[0]])
                if(form.cleaned_data['Check'+sub[0]]):
                    if(form.cleaned_data['RadioMode'+sub[0]]==1):
                        studyModeCredits += sub[2]
                    else:
                        examModeCredits += sub[2]
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        if(form.cleaned_data['Check'+sub[0]]):
                            #regular registration record is already existed
                            pass
                        else:
                            #delete regular_record from the registration table 
                            StudentRegistrations.objects.filter(RegNo = request.POST['RegNo'], SubCode = sub[0]).delete()
                    else:   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+sub[0]])):
                            #update operation mode could be study mode or exam mode

                            StudentRegistrations.objects.filter(RegNo = request.POST['RegNo'], SubCode = sub[0]).update(Mode=form.cleaned_data['RadioMode'+sub[0]])
                        elif(sub[5]):
                            #delete record from registration table
                            StudentRegistrations.objects.filter(RegNo = request.POST['RegNo'], SubCode = sub[0]).delete()
                        elif(form.cleaned_data['Check'+sub[0]]):
                            #insert backlog registration
                            newRegistration = StudentRegistrations(RegNo = request.POST['RegNo'],SubCode=sub[0],AYear=ayear,ASem=asem,OfferedYear=sub[7],Dept=dept,BYear=byear,Regulation=sub[8],BSem=bsem,Mode=form.cleaned_data['RadioMode'+sub[0]])
                            newRegistration.save()                   
                return(render(request,'SupExamDBRegistrations/BTBacklogRegistrationSuccess.html'))    
            else:
                print("Number of credits exceeded")
        else:
            print("form validation failed")             
    else:
        form = BacklogRegistrationForm()
    context = {'form':form}
    if(len(studentInfo)!=0):
        context['RollNo'] = studentInfo[0].RollNo
        context['Name'] = studentInfo[0].Name  
    print(request.POST)
    return render(request, 'SupExamDBRegistrations/BTBacklogRegistration.html',context)

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def makeup_registration_info(request):
    programmeList = ProgrammeModel.objects.filter(ProgrammeName='B.Tech.')
    yearList = [1,2,3,4]
    
    if(request.method=='POST'):
        form = DeptYearSelectionForm(request.POST)
        if(form.is_valid()):
            print(form.cleaned_data['deptBox'])
            print(form.cleaned_data['yearBox'])
            return HttpResponseRedirect(reverse('DeptYearRegistrationStatus',args=(form.cleaned_data['yearBox'],form.cleaned_data['deptBox'],)))
    else:
        form = DeptYearSelectionForm()
    return render(request,'SupExamDBRegistrations/MakeupRegistrationInfo.html',{'programmeList': programmeList, 'yearList': yearList, 'form':form })

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
            #print(regno, currentDept, newDept, ayear)
            if currentDept != newDept:
                newRow = BranchChanges(RegNo=regno, RollNo=rollno, CurrentDept=currentDept, NewDept=newDept, AYear=ayear)
                newRow.save()
                StudentInfo.objects.filter(RegNo=regno).update(Dept=newDept)
                print(newRow)
                context['regno']=regno
                context['Name'] = name
                context['dept'] = newDept
                return render(request,'SupExamDBRegistrations/BTBranchChangeSuccess.html',context )
        else:
            print("form is not valid")
    else:
        form = BranchChangeForm()
    context['form']= form   
    return render(request,'SupExamDBRegistrations/BTBranchChange.html', context)

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
            results = BranchChanges.objects.filter(AYear=ayear).values()
            context['ayear'] = ayear
            context['rows'] = results
            return render(request, 'SupExamDBRegistrations/BTBranchChangeStatus.html', context)
        else:
            print('form validation failed')        
    else:
        form = BranchChangeStausForm()
    context['form'] = form
    return render(request, 'SupExamDBRegistrations/BTBranchChangeStatus.html', context)