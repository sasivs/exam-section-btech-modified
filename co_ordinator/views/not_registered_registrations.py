from django.contrib.auth.decorators import login_required, user_passes_test
from SupExamDBRegistrations.views.home import is_Superintendent
from django.shortcuts import render
from hod.models import Coordinator
from ExamStaffDB.models import StudentInfo
from co_ordinator.models import Subjects, StudentRegistrations_Staging, DroppedRegularCourses
from co_ordinator.forms import NotRegisteredRegistrationsForm
from superintendent.models import RegistrationStatus, CycleCoordinator


@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def not_registered_registrations(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    coordinator = None
    if 'Co-ordinator' in groups:
        coordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear,Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1,Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    studentInfo = []
    if(request.method == 'POST'):
        currentRegEventId = request.POST.get('regEvent')
        # con = {key:request.POST[key] for key in request.POST.keys()} 
        # if('RegNo' in request.POST.keys()):
        #     droppedCourses = DroppedRegularCourses.objects.filter(RegNo=request.POST['RegNo'])
        #     reg_status = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem, Regulation=regulation)
        #     studentRegistrations=[]
        #     for regevent in reg_status:
        #         studentRegistrations += list(StudentRegistrations_Staging.objects.filter(RegNo=request.POST['RegNo'],RegEventId=regevent.id))
        #     studentRegularRegistrations = []
        #     for regn in studentRegistrations:
        #         regEvent = RegistrationStatus.objects.get(id=regn.RegEventId)
        #         if (regEvent.Mode == 'R' or regEvent.Mode == 'D'):
        #             studentRegularRegistrations.append(regn)
        #     for row in droppedCourses:
        #         for entry in studentRegistrations:
        #             if row.sub_id == entry. sub_id:
        #                 con[str('RadioMode'+row.sub_id)] = list(str(entry.Mode))

        form = NotRegisteredRegistrationsForm(regIDs,coordinator, request.POST)
        if not request.POST.get('regd_no'):
            pass 
        elif not 'submit' in request.POST.keys():
            regNo = request.POST['regd_no']
            event = request.POST['regEvent']
            studentInfo = StudentInfo.objects.filter(RegNo=regNo)
        elif('regEvent' in request.POST and 'regd_no' in request.POST and 'submit' in request.POST and form.is_valid()):
            regNo = request.POST['regd_no']
            event = request.POST['regEvent']
            studentInfo = StudentInfo.objects.filter(RegNo=regNo) 
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
                        if(len(studentInfo)!=0):
                            context['RollNo'] = studentInfo[0].RollNo
                            context['Name'] = studentInfo[0].Name  
                        return render(request, 'SupExamDBRegistrations/DroppedRegularReg.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        regular_sub = Subjects.objects.get(id=sub[9])
                        if(form.cleaned_data['Check'+str(sub[9])] == False):
                            #delete regular_record from the registration table
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=request.POST.get('regEvent'),\
                                 sub_id = sub[9], id=sub[10])
                            if len(reg) != 0:
                                StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=request.POST.get('regEvent'),\
                                     sub_id = sub[9], id=sub[10]).delete()
                                new_dropped_course = DroppedRegularCourses(RegNo=request.POST['RegNo'], sub_id=sub[9])
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if(len(reg) == 0):
                                newRegistration = StudentRegistrations_Staging(RegNo = request.POST['RegNo'], RegEventId = currentRegEventId,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                                newRegistration.save()
                        else:
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if len(reg) != 0:
                                StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                     sub_id = sub[9]).delete()
                    elif sub[6] == 'B':   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+sub[0]])
                        elif(sub[5]):
                            #delete record from registration table
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], id=sub[10]).delete()  
                    
                    elif sub[6] == 'NR':
                        if(form.cleaned_data['Check'+str(sub[9])]):
                            reg = StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], RegEventId=currentRegEventId,\
                                 sub_id = sub[9])
                            if not reg:
                                newRegistration = StudentRegistrations_Staging(RegNo = request.POST['RegNo'], RegEventId = currentRegEventId,\
                                    Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                                newRegistration.save()
                    msg = 'Registrations done successfully'
                return render(request,'co_ordinator/NotRegisteredRegistrations.html', {'form':form, 'msg':msg})
            else:
                form = NotRegisteredRegistrationsForm(regIDs,coordinator, request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(len(studentInfo)!=0):
                    context['RollNo'] = studentInfo[0].RollNo
                    context['Name'] = studentInfo[0].Name  
                return render(request, 'co_ordinator/NotRegisteredRegistrations.html',context)
        else:
            print("form validation failed")             
    else:
        form = NotRegisteredRegistrationsForm(regIDs,coordinator)
    context = {'form':form}
    if(len(studentInfo)!=0):
        context['RollNo'] = studentInfo[0].RollNo
        context['Name'] = studentInfo[0].Name  
    return render(request, 'co_ordinator/NotRegisteredRegistrations.html',context)