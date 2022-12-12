from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import registration_access
from BTco_ordinator.forms import BacklogRegistrationForm
from BTco_ordinator.models import BTStudentBacklogs, BTStudentRegistrations_Staging, BTDroppedRegularCourses, BTRollLists_Staging
from ADAUGDB.models import BTCycleCoordinator
from BThod.models import BTCoordinator
from ADAUGDB.models import BTRegistrationStatus
from BTExamStaffDB.models import BTStudentInfo
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(registration_access)
def btech_backlog_registration(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='B')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='B')
    studentInfo = []
    if(request.method == 'POST'):
        event = BTRegistrationStatus.objects.filter(id=request.POST.get('RegEvent')).first()
        con = {} 
        if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
            con['RegEvent']=request.POST['RegEvent']
            if 'RegNo' in request.POST.keys():
                con['RegNo']=request.POST['RegNo']
            form = BacklogRegistrationForm(regIDs,con)
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
            form = BacklogRegistrationForm(regIDs, request.POST)
        if not 'RegNo' in request.POST.keys():
            pass 
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and not 'Submit' in request.POST:
            roll = BTRollLists_Staging.objects.filter(id=request.POST.get('RegNo')).first()
            studentRegistrations = BTStudentRegistrations_Staging.objects.filter(student=roll, \
                RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__Regulation=event.Regulation)
            mode_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in studentRegistrations}
            student_obj = roll.student
            context = {'form':form, 'msg':0}
            context['RollNo'] = student_obj.RollNo
            context['Name'] = student_obj.Name  
            from json import dumps
            context['modes'] = dumps(mode_selection)
            return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)
        elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
            roll = BTRollLists_Staging.objects.filter(id=request.POST.get('RegNo')).first()
            studentInfo = roll.student
            studyModeCredits = 0
            examModeCredits = 0
            for sub in form.myFields:
                if(form.cleaned_data['Check'+str(sub[9])]):
                    if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
                        if(form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
                            studyModeCredits += sub[2]
                        else:
                            examModeCredits += sub[2]
                    else:
                        form = BacklogRegistrationForm(regIDs, request.POST)
                        context = {'form':form, 'msg': 2}  
                        if(len(studentInfo)!=0):
                            context['RollNo'] = studentInfo.RollNo
                            context['Name'] = studentInfo.Name  
                        return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        # for regular and dropped there is no need to check if it is selected!!!
                        if form.cleaned_data['Check'+str(sub[9])] == False:   #delete regular_record from the registration table
                            reg = BTStudentRegistrations_Staging.objects.filter(id=sub[10])
                            if len(reg) != 0:
                                BTStudentRegistrations_Staging.objects.get(id=sub[10]).delete()
                                new_dropped_course = BTDroppedRegularCourses(student=studentInfo, subject_id=sub[9], RegEventId_id=reg.RegEventId.id, Registered=False)
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if form.cleaned_data['Check'+str(sub[9])] == False:
                            BTStudentRegistrations_Staging.objects.filter(id=sub[10]).delete()
                            BTDroppedRegularCourses.objects.filter(student=studentInfo, subject_id=sub[9]).update(Registered=False)
                    else:   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            BTStudentRegistrations_Staging.objects.filter(student=roll, \
                                sub_id_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+str(sub[9])])
                        elif(sub[5]):
                            #delete record from registration table
                            BTStudentRegistrations_Staging.objects.filter(id=sub[10]).delete()
                        elif(form.cleaned_data['Check'+str(sub[9])]):
                            #insert backlog registration
                            if sub[10]=='':
                                newRegistration = BTStudentRegistrations_Staging(student_id=form.cleaned_data['RegNo'],RegEventId_id=event.id,\
                                Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id_id=sub[9])
                                newRegistration.save()                   
                return(render(request,'BTco_ordinator/BTBacklogRegistrationSuccess.html'))
            else:
                form = BacklogRegistrationForm(regIDs, request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(len(studentInfo)!=0):
                    context['RollNo'] = studentInfo.RollNo
                    context['Name'] = studentInfo.Name  
                return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)
        
    else:
        form = BacklogRegistrationForm(regIDs)
    context = {'form':form, 'msg':0}
    if(len(studentInfo)!=0):
        context['RollNo'] = studentInfo.RollNo
        context['Name'] = studentInfo.Name  
    return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)

def backlog_registrations(file):
    import pandas as pd
    file = pd.read_excel(file)
    for rIndex, row in file.iterrows():
        print(row)
        if row[2] == 1:
            backlogs = BTStudentBacklogs.objects.filter(RegNo=row[9], BYear=row[2], Dept=row[4])
        else:
            backlogs = BTStudentBacklogs.objects.filter(RegNo=row[9], BYear=row[2], Dept=row[4], BSem=row[3])
        regEventId = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
        subject_id = backlogs.filter(SubCode=row[7]).first()
        if not BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).exists():
            registration_obj = BTStudentRegistrations_Staging(student__student__RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row[8])
            registration_obj.save()
        else:
            BTStudentRegistrations_Staging.objects.filter(RegNo=row[9], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).update(Mode=row[8])
    return "Completed!!"



