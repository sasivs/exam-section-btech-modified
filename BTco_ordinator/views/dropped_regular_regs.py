from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import DroppedRegularRegistrationsForm
from BTco_ordinator.models import BTDroppedRegularCourses, BTStudentRegistrations_Staging, BTRollLists_Staging
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.models import BTCycleCoordinator
from BTExamStaffDB.models import BTStudentInfo
from BThod.models import BTCoordinator

@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dropped_regular_registrations(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='D')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='D')
    studentInfo = []
    if(request.method == 'POST'):
        event = BTRegistrationStatus.objects.filter(id=request.POST.get('RegEvent'))
        con = {key:request.POST[key] for key in request.POST.keys()} 
        if('RegNo' in request.POST.keys()):
            roll = BTRollLists_Staging.objects.filter(id=request.POST['RegNo']).first()
            droppedCourses = BTDroppedRegularCourses.objects.filter(student=roll.student)
            studentRegistrations = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=roll.student.RegNo,RegEventId__AYear=event.AYear, \
                    RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation)

            for row in droppedCourses:
                for entry in studentRegistrations:
                    if row.sub_id == entry. sub_id:
                        con[str('RadioMode'+row.sub_id)] = list(str(entry.Mode))

        form = DroppedRegularRegistrationsForm(regIDs,con)
        if not 'RegNo' in request.POST.keys():
            pass 
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and not 'Submit' in request.POST:
            roll = BTRollLists_Staging.objects.filter(id=request.POST['RegNo']).first()
            studentRegistrations = BTStudentRegistrations_Staging.objects.filter(student=roll, RegEventId__AYear=event.AYear, \
                    RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation)
            mode_selection = {'RadioMode'+str(reg.sub_id): reg.Mode for reg in studentRegistrations}
            student_obj = roll.student
            context = {'form':form, 'msg':0}
            context['RollNo'] = student_obj.RollNo
            context['Name'] = student_obj.Name  
            from json import dumps
            context['modes'] = dumps(mode_selection)
            return render(request, 'BTco_ordinator/DroppedRegularReg.html',context)
        elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
            event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('RegEvent'))
            roll = BTRollLists_Staging.objects.filter(id=form.cleaned_data['RegNo']).first()
            studentInfo = roll.student
            studyModeCredits = 0
            examModeCredits = 0
            for sub in form.myFields:
                if(form.cleaned_data['Check'+str(sub[9])]):
                    if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
                        if (form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
                            studyModeCredits += sub[2]
                        else:
                            examModeCredits += sub[2]
                    else:
                        form = DroppedRegularRegistrationsForm(regIDs,request.POST)
                        context = {'form':form, 'msg': 2}  
                        if(len(studentInfo)!=0):
                            context['RollNo'] = studentInfo.RollNo
                            context['Name'] = studentInfo.Name  
                        return render(request, 'BTco_ordinator/DroppedRegularReg.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        if(form.cleaned_data['Check'+str(sub[9])] == False):
                            #delete regular_record from the registration table
                            reg = BTStudentRegistrations_Staging.objects.filter(id=sub[10])
                            if len(reg) != 0:
                                BTStudentRegistrations_Staging.objects.filter(id=sub[10]).delete()
                                new_dropped_course = BTDroppedRegularCourses(student=studentInfo, subject_id=sub[9], RegEventId_id=reg.RegEventId, Registered=False)
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = BTStudentRegistrations_Staging.objects.filter(student=roll, RegEventId=event,\
                                 sub_id_id = sub[9])
                            if(len(reg) == 0):
                                newRegistration = BTStudentRegistrations_Staging(student=roll,  RegEventId=event,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id_id=sub[9])
                                newRegistration.save()
                                BTDroppedRegularCourses.objects.filter(student=studentInfo, subject_id=sub[9]).update(Registered=True)
                        else:
                            if sub[10]:
                                reg = BTStudentRegistrations_Staging.objects.filter(id=sub[10])
                                if len(reg) != 0:
                                    BTStudentRegistrations_Staging.objects.filter(id=sub[10]).delete()
                                    BTDroppedRegularCourses.objects.filter(student=studentInfo, subject_id=sub[9]).update(Registered=False)
                    else:   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            BTStudentRegistrations_Staging.objects.filter(student=roll, sub_id_id=sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+sub[0]])
                        elif(sub[5]):
                            #delete record from registration table
                            BTStudentRegistrations_Staging.objects.filter(student=roll, sub_id_id = sub[9], id=sub[10]).delete()  
                return(render(request,'BTco_ordinator/DroppedRegularRegSuccess.html'))
            else:
                form = DroppedRegularRegistrationsForm(regIDs,request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(len(studentInfo)!=0):
                    context['RollNo'] = studentInfo.RollNo
                    context['Name'] = studentInfo.Name  
                return render(request, 'BTco_ordinator/DroppedRegularReg.html',context)
        else:
            print("form validation failed")             
    else:
        form = DroppedRegularRegistrationsForm(regIDs)
    context = {'form':form}
    if(len(studentInfo)!=0):
        context['RollNo'] = studentInfo.RollNo
        context['Name'] = studentInfo.Name  
    return render(request, 'BTco_ordinator/DroppedRegularReg.html',context)
