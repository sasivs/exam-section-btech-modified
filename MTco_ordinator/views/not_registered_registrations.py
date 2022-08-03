from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from MThod.models import MTCoordinator
from MTExamStaffDB.models import MTStudentInfo
from MTco_ordinator.models import MTNotRegistered, MTSubjects, MTStudentRegistrations_Staging
from MTco_ordinator.forms import NotRegisteredRegistrationsForm
from MTsuperintendent.models import MTRegistrationStatus
from MTsuperintendent.user_access_test import registration_access


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def not_registered_registrations(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    coordinator = None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear,Mode='R')
   
    studentInfo = []
    if(request.method == 'POST'):
        currentRegEventId = request.POST.get('regEvent')
        form = NotRegisteredRegistrationsForm(regIDs, request.POST)
        if not request.POST.get('regd_no'):
            pass 
        elif not 'submit-form' in request.POST.keys():
            regNo = request.POST['regd_no']
            event = request.POST['regEvent']
            studentInfo = MTNotRegistered.objects.filter(id=regNo).first()
        elif(request.POST.get('regEvent') and request.POST.get('regd_no') and 'submit-form' in request.POST.keys() and form.is_valid()):
            regNo = request.POST['regd_no']
            event = request.POST['regEvent']
            studentInfo = MTNotRegistered.objects.filter(id=regNo).first()
            regNo = MTstudentInfo.Student.RegNo
            # studyModeCredits = 0
            # examModeCredits = 0
            # for sub in form.myFields:
            #     if(form.cleaned_data['Check'+str(sub[9])]):
            #         if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
            #             if (form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
            #                 studyModeCredits += sub[2]
            #             else:
            #                 examModeCredits += sub[2]
            #         else:
            #             form = NotRegisteredRegistrationsForm(regIDs,coordinator, request.POST)
            #             context = {'form':form, 'msg': 2}  
            #             if(studentInfo):
            #                 context['RollNo'] = studentInfo.Student.RollNo
            #                 context['Name'] = studentInfo.Student.Name  
            #             return render(request, 'SupExamDBRegistrations/DroppedRegularReg.html',context)
            # if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
            for sub in form.myFields:
                # if(sub[6]=='R'): #Handling Regular Subjects
                #     regular_sub = MTSubjects.objects.get(id=sub[9])
                #     if(form.cleaned_data['Check'+str(sub[9])] == False):
                #         #delete regular_record from the registration table
                #         reg = MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=request.POST.get('regEvent'),\
                #                 sub_id = sub[9], id=sub[10])
                #         if len(reg) != 0:
                #             MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=request.POST.get('regEvent'),\
                #                     sub_id = sub[9], id=sub[10]).delete()
                #             new_dropped_course = MTDroppedRegularCourses(student=studentInfo.Student, subject_id=sub[9], RegEventId_id=event, Registered=False)
                #             new_dropped_course.save()
                # elif sub[6] == 'D':
                #     if(form.cleaned_data['Check'+str(sub[9])]):
                #         reg = MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                #                 sub_id = sub[9])
                #         if(len(reg) == 0):
                #             newRegistration = MTStudentRegistrations_Staging(RegNo=regNo, RegEventId = currentRegEventId,\
                #                 Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                #             newRegistration.save()
                #             MTDroppedRegularCourses.objects.filter(student=studentInfo.Student, subject_id=sub[9]).update(Registered=True)
                    # else:
                    #     reg = MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                    #             sub_id = sub[9])
                    #     if len(reg) != 0:
                    #         MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                    #                 sub_id = sub[9]).delete()
                    #         MTDroppedRegularCourses.objects.filter(student=studentInfo.Student, subject_id=sub[9]).update(Registered=False)
                # elif sub[6] == 'B':   #Handling Backlog Subjects
                #     if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                #         #update operation mode could be study mode or exam mode
                #         MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+sub[0]])
                #     elif(sub[5]):
                #         #delete record from registration table
                #         MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, sub_id = sub[9], id=sub[10]).delete()  
                
                if sub[6] == 'NR':
                    if(form.cleaned_data['Check'+str(sub[9])]):
                        reg = MTStudentRegistrations_Staging.objects.filter(RegNo=regNo, RegEventId=currentRegEventId,\
                                sub_id = sub[9])
                        if not reg:
                            newRegistration = MTStudentRegistrations_Staging(RegNo=regNo, RegEventId = currentRegEventId,\
                                Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                            newRegistration.save()
                msg = 'Registrations have been done successfully'
            return render(request,'MTco_ordinator/NotRegisteredRegistrations.html', {'msg':msg})
            # else:
            #     form = NotRegisteredRegistrationsForm(regIDs, request.POST)
            #     context = {'form':form, 'msg':1}
            #     context['study']=studyModeCredits
            #     context['exam']=examModeCredits
            #     if(studentInfo):
            #         context['RollNo'] = studentInfo.Student.RollNo
            #         context['Name'] = studentInfo.Student.Name  
            #     return render(request, 'MTco_ordinator/NotRegisteredRegistrations.html',context)
  
    else:
        form = NotRegisteredRegistrationsForm(regIDs)
    context = {'form':form}
    if(studentInfo):
        context['RollNo'] = studentInfo.Student.RegNo
        context['Name'] = studentInfo.Student.Name  
    return render(request, 'MTco_ordinator/NotRegisteredRegistrations.html',context)
