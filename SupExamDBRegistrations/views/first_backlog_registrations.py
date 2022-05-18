from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.shortcuts import redirect
from django.urls import reverse
from SupExamDBRegistrations.forms import FirstYearBacklogRegistrationForm
from SupExamDBRegistrations.models import StudentBacklogs, StudentInfo, StudentRegistrations
from .home import is_Superintendent
from django.db.models import F


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def btech_first_year_backlog_Registrations(request):
    studentInfo = []
    if request.method == 'POST':
        if 'RegEvent' in request.POST.keys():
            event = request.POST['RegEvent']
            eventDetails = event.split('-')
            romans2int = {"I":1,"II":2,"III":3,"IV":4}
            byear = romans2int[eventDetails[3]]
            ayear = int(eventDetails[1])
            asem = romans2int[eventDetails[2]]
            bsem = romans2int[eventDetails[4]]
            con = {key:request.POST[key] for key in request.POST.keys()}
        if 'RegNo' in request.POST.keys():
            print(request.POST)
            studentBacklogs = StudentBacklogs.objects.filter(RegNo=request.POST['RegNo']).filter(BYear = byear)
            studentRegistrations = StudentRegistrations.objects.filter(RegNo=request.POST['RegNo'],AYear=ayear,ASem=asem)
            #Selection={studentRegistrations[i].SubCode:studentRegistrations[i].Mode for i in range(len(studentRegistrations))}
            studentRegularRegistrations = studentRegistrations.filter(AYear= F('OfferedYear'))
            for row in studentBacklogs:
                print(row.SubCode)
                studentRegularRegistrations = studentRegularRegistrations.values()
                for entry in studentRegularRegistrations:
                    print(entry)
                    if row.SubCode == entry['SubCode']:
                        con[str('RadioMode'+row.SubCode)] = list(str(entry['Mode']))
        form = FirstYearBacklogRegistrationForm(con)
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
                            dept = StudentBacklogs.objects.filter(RegNo=request.POST['RegNo']).filter(BYear = byear).filter(SubCode=sub[0]).values()
                            print(dept)
                            newRegistration = StudentRegistrations(RegNo = request.POST['RegNo'],SubCode=sub[0],AYear=ayear,ASem=asem,OfferedYear=sub[7],Dept = dept[0]['Dept'],BYear=byear,Regulation=sub[8],BSem=bsem,Mode=form.cleaned_data['RadioMode'+sub[0]])
                            newRegistration.save()                   
                return(render(request,'SupExamDBRegistrations/BTBacklogRegistrationSuccess.html'))    
            else:
                print("Number of credits exceeded")
        else:
            print("form validation failed")        
    else:
        form = FirstYearBacklogRegistrationForm()
    context = {'form':form}

    if(len(studentInfo)!=0):
        if studentInfo[0].RollNo:
            context['RollNo'] = studentInfo[0].RollNo
        else:
            context['RegNo'] = studentInfo[0].RegNo
        context['Name'] = studentInfo[0].Name  
        
    print(request.POST)
    return render(request, 'SupExamDBRegistrations/BTFirstYearBacklogRegistration.html', context)
