from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from hod.models import BTCoordinator
from ExamStaffDB.models import BTStudentInfo
from BTco_ordinator.models import BTNotRegistered, BTSubjects, BTStudentRegistrations_Staging, BTDroppedRegularCourses
from BTco_ordinator.forms import NotRegisteredRegistrationsForm
from superintendent.models import BTRegistrationStatus, BTCycleCoordinator
from superintendent.user_access_test import registration_access


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def not_registered_registrations(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    coordinator = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear,Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1,Mode='R')
    studentInfo = []
    if(request.method == 'POST'):
        currentRegEventId = request.POST.get('regEvent')
        form = NotRegisteredRegistrationsForm(regIDs, request.POST)
        if not request.POST.get('regd_no'):
            pass 
        elif not 'submit-form' in request.POST.keys():
            regNo = request.POST['regd_no']
            event = request.POST['regEvent']
            studentInfo = BTNotRegistered.objects.filter(id=regNo).first()
        elif(request.POST.get('regEvent') and request.POST.get('regd_no') and 'submit-form' in request.POST.keys() and form.is_valid()):
            regNo = request.POST['regd_no']
            event = request.POST['regEvent']
            studentInfo = BTNotRegistered.objects.filter(id=regNo).first()
            regNo = studentInfo.Student.RegNo
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
                        form = NotRegisteredRegistrationsForm(regIDs,coordinator, request.POST)
                        context = {'form':form, 'msg': 2}  
                        if(studentInfo):
                            context['RollNo'] = studentInfo.Student.RollNo
                            context['Name'] = studentInfo.Student.Name  
                        return render(request, 'SupExamDBRegistrations/DroppedRegularReg.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        regular_sub = BTSubjects.objects.get(id=sub[9])
                        if(form.cleaned_data['Check'+str(sub[9])] == False):
                            #delete regular_record from the registration table
                            reg = BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=request.POST.get('regEvent'),\
                                 sub_id = sub[9], id=sub[10])
                            if len(reg) != 0:
                                BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=request.POST.get('regEvent'),\
                                     sub_id = sub[9], id=sub[10]).delete()
                                new_dropped_course = BTDroppedRegularCourses(student=studentInfo.Student, subject_id=sub[9], RegEventId_id=event, Registered=False)
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if(len(reg) == 0):
                                newRegistration = BTStudentRegistrations_Staging(RegNo=regNo, RegEventId = currentRegEventId,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                                newRegistration.save()
                                BTDroppedRegularCourses.objects.filter(student=studentInfo.Student, subject_id=sub[9]).update(Registered=True)
                        else:
                            reg = BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if len(reg) != 0:
                                BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                                     sub_id = sub[9]).delete()
                                BTDroppedRegularCourses.objects.filter(student=studentInfo.Student, subject_id=sub[9]).update(Registered=False)
                    elif sub[6] == 'B':   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+sub[0]])
                        elif(sub[5]):
                            #delete record from registration table
                            BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, sub_id = sub[9], id=sub[10]).delete()  
                    
                    elif sub[6] == 'NR':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = BTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if not reg:
                                newRegistration = BTStudentRegistrations_Staging(RegNo=regNo, RegEventId = currentRegEventId,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                                newRegistration.save()
                    msg = 'Registrations have been done successfully'
                return render(request,'co_ordinator/NotRegisteredRegistrations.html', {'msg':msg})
            else:
                form = NotRegisteredRegistrationsForm(regIDs, request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(studentInfo):
                    context['RollNo'] = studentInfo.Student.RollNo
                    context['Name'] = studentInfo.Student.Name  
                return render(request, 'co_ordinator/NotRegisteredRegistrations.html',context)
  
    else:
        form = NotRegisteredRegistrationsForm(regIDs)
    context = {'form':form}
    if(studentInfo):
        context['RollNo'] = studentInfo.Student.RollNo
        context['Name'] = studentInfo.Student.Name  
    return render(request, 'co_ordinator/NotRegisteredRegistrations.html',context)
