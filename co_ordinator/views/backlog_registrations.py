from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from superintendent.user_access_test import registration_access
from co_ordinator.forms import BacklogRegistrationForm
from co_ordinator.models import Subjects, StudentRegistrations_Staging, DroppedRegularCourses
from superintendent.models import RegistrationStatus, CycleCoordinator
from hod.models import Coordinator
from ExamStaffDB.models import StudentInfo


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def btech_backlog_registration(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='B')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = RegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=cycle_cord.Cycle, BYear=1, Mode='B')
    studentInfo = []
    if(request.method == 'POST'):
        regId = request.POST['RegEvent']
        strs = regId.split(':')
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2,'III':3,'IV':4}
        strs = regId.split(':')
        dept = deptDict[strs[0]]
        ayear = int(strs[3])
        asem = int(strs[4])
        byear = rom2int[strs[1]]
        bsem = rom2int[strs[2]]
        regulation = int(strs[5])
        mode = strs[6]
        currentRegEventId = RegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
        currentRegEventId = currentRegEventId[0].id
        con = {} 
        if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
            con['RegEvent']=request.POST['RegEvent']
            if 'RegNo' in request.POST.keys():
                con['RegNo']=request.POST['RegNo']
            form = BacklogRegistrationForm(regIDs,con)
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
            form = BacklogRegistrationForm(request.POST)
        if not 'RegNo' in request.POST.keys():
            pass 
        elif not 'Submit' in request.POST.keys():
            regNo = request.POST['RegNo']
            event = (request.POST['RegEvent'])
            print(regNo, event)
            studentInfo = StudentInfo.objects.filter(RegNo=regNo)
        elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
            regNo = request.POST['RegNo']
            event = (request.POST['RegEvent'])
            studentInfo = StudentInfo.objects.filter(RegNo=regNo) 
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
                        form = BacklogRegistrationForm(request.POST)
                        context = {'form':form, 'msg': 2}  
                        if(len(studentInfo)!=0):
                            context['RollNo'] = studentInfo[0].RollNo
                            context['Name'] = studentInfo[0].Name  
                        return render(request, 'co_ordinator/BTBacklogRegistration.html',context)
            if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
                for sub in form.myFields:
                    if(sub[6]=='R'): #Handling Regular Subjects
                        regular_sub = Subjects.objects.get(id=sub[9])
                        # for regular and dropped there is no need to check if it is selected!!!
                        if form.cleaned_data['Check'+str(sub[9])] == False:   #delete regular_record from the registration table
                            reg = StudentRegistrations_Staging.objects.\
                                filter(RegNo = request.POST['RegNo'], RegEventId=regular_sub.RegEventId_id,sub_id = sub[9], id=sub[10])
                            if len(reg) != 0:
                                StudentRegistrations_Staging.objects.get(RegNo = request.POST['RegNo'], RegEventId=regular_sub.RegEventId_id,\
                                     sub_id = sub[9], id=sub[10]).delete()
                                new_dropped_course = DroppedRegularCourses(RegNo=request.POST['RegNo'], sub_id=sub[9])
                                new_dropped_course.save()
                    elif sub[6] == 'D':
                        if form.cleaned_data['Check'+str(sub[9])] == False:
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], \
                                id=sub[10]).delete()
                    else:   #Handling Backlog Subjects
                        if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                            #update operation mode could be study mode or exam mode
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], \
                                sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+str(sub[9])])
                        elif(sub[5]):
                            #delete record from registration table
                            StudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], \
                                sub_id = sub[9], id=sub[10]).delete()
                        elif(form.cleaned_data['Check'+str(sub[9])]):
                            #insert backlog registration
                            if sub[10]=='':
                                newRegistration = StudentRegistrations_Staging(RegNo = request.POST['RegNo'],RegEventId=currentRegEventId,\
                                Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                                newRegistration.save()                   
                return(render(request,'co_ordinator/BTBacklogRegistrationSuccess.html'))
            else:
                form = BacklogRegistrationForm(request.POST)
                context = {'form':form, 'msg':1}
                context['study']=studyModeCredits
                context['exam']=examModeCredits
                if(len(studentInfo)!=0):
                    context['RollNo'] = studentInfo[0].RollNo
                    context['Name'] = studentInfo[0].Name  
                return render(request, 'co_ordinator/BTBacklogRegistration.html',context)
        else:
            print("form validation failed")   
            print(form.errors.as_data())          
    else:
        form = BacklogRegistrationForm(regIDs)
    context = {'form':form, 'msg':0}
    if(len(studentInfo)!=0):
        context['RollNo'] = studentInfo[0].RollNo
        context['Name'] = studentInfo[0].Name  
    return render(request, 'co_ordinator/BTBacklogRegistration.html',context)


