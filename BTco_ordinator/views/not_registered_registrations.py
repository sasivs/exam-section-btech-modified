from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from BThod.models import BTCoordinator
from BTExamStaffDB.models import BTStudentInfo
from BTco_ordinator.models import BTNotRegistered, BTSubjects, BTStudentRegistrations_Staging, BTDroppedRegularCourses
from BTco_ordinator.forms import NotRegisteredRegistrationsForm
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTCycleCoordinator
from BTsuperintendent.user_access_test import registration_access


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
        form = NotRegisteredRegistrationsForm(regIDs, request.POST)
        if not request.POST.get('regd_no'):
            pass 
        elif(request.POST.get('regEvent') and request.POST.get('regd_no') and not 'submit-form' in request.POST.keys()):
            event = BTRegistrationStatus.objects.get(id=event)
            not_registered_student = BTNotRegistered.objects.filter(id=request.POST['regd_no']).first()

            regEvents = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=event.ASem, Regulation=event.Regulation)
            studentRegistrations = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=not_registered_student.Student.RegNo, \
                RegEventId__in=regEvents.values_list('id', flat=True))
            mode_selection = {'RadioMode'+str(reg.sub_id_id): reg.Mode for reg in studentRegistrations}

            context = {'form':form, 'msg':0}
            context['RollNo'] = not_registered_student.Student.RollNo
            context['Name'] = not_registered_student.Student.Name  
            from json import dumps
            context['modes'] = dumps(mode_selection)
            return render(request, 'BTco_ordinator/NotRegisteredRegistrations.html',context)
        elif(request.POST.get('regEvent') and request.POST.get('regd_no') and 'submit-form' in request.POST.keys() and form.is_valid()):
            event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regEvent'))
            studentInfo = BTNotRegistered.objects.filter(id=form.cleaned_data.get('regd_no')).first()
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
                        return render(request, 'BTco_ordinator/DroppedRegularReg.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        if(form.cleaned_data['Check'+str(sub[9])] == False):
                            #delete regular_record from the registration table
                            reg = BTStudentRegistrations_Staging.objects.filter(student__student=studentInfo.Student, RegEventId_id=event.id,\
                                 sub_id_id = sub[9], id=sub[10])
                            if len(reg) != 0:
                                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, RegEventId_id=event.id,\
                                     sub_id_id = sub[9], id=sub[10]).delete()
                                new_dropped_course = BTDroppedRegularCourses(student=studentInfo.Student, subject_id=sub[9], RegEventId_id=event.id, Registered=False)
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if(form.cleaned_data['Check'+str(sub[9])]==False):
                            reg = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo,\
                                 sub_id_id = sub[9], id=sub[10])
                            if len(reg) != 0:
                                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, id=sub[10],\
                                     sub_id_id = sub[9]).delete()
                                BTDroppedRegularCourses.objects.filter(student=studentInfo.Student, subject_id=sub[9]).update(Registered=False)
                    elif sub[6] == 'B':   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, sub_id_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+sub[9]])
                        elif(sub[5]):
                            #delete record from registration table
                            BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, sub_id_id = sub[9], id=sub[10]).delete()  
                    
                    elif sub[6] == 'NR':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, RegEventId_id=event.id,\
                                 sub_id_id = sub[9])
                            if not reg:
                                newRegistration = BTStudentRegistrations_Staging(student=studentInfo.Student, RegEventId_id=event.id,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id_id=sub[9])
                                newRegistration.save()
                                BTDroppedRegularCourses.objects.filter(student=studentInfo.Student, subject_id=sub[9]).delete()
                        else:
                            reg = BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, RegEventId=event.id,\
                                 sub_id_id = sub[9])
                            if reg:
                                BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=studentInfo.Student.RegNo, RegEventId=event.id,\
                                 sub_id_id = sub[9]).delete()
                                new_dropped_course = BTDroppedRegularCourses(student=studentInfo.Student, subject_id=sub[9], RegEventId_id=event.id, Registered=False)
                                new_dropped_course.save()
                            
                    msg = 'Registrations have been done successfully'
                return render(request,'BTco_ordinator/NotRegisteredRegistrations.html', {'msg':msg})
            else:
                form = NotRegisteredRegistrationsForm(regIDs, request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(studentInfo):
                    context['RollNo'] = studentInfo.Student.RollNo
                    context['Name'] = studentInfo.Student.Name  
                return render(request, 'BTco_ordinator/NotRegisteredRegistrations.html',context)
  
    else:
        form = NotRegisteredRegistrationsForm(regIDs)
    context = {'form':form}
    if(studentInfo):
        context['RollNo'] = studentInfo.Student.RollNo
        context['Name'] = studentInfo.Student.Name  
    return render(request, 'BTco_ordinator/NotRegisteredRegistrations.html',context)
