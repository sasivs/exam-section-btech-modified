from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTsuperintendent.user_access_test import registration_access
from MTco_ordinator.forms import BacklogRegistrationForm
from MTco_ordinator.models import MTSubjects, MTStudentRegistrations_Staging
from MTsuperintendent.models import MTRegistrationStatus
from MThod.models import MTCoordinator
from MTExamStaffDB.models import MTStudentInfo


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def mtech_backlog_registration(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, MTProgrammeModel=1, Dept=coordinator.Dept, MYear=coordinator.MYear, Mode='B')
    studentInfo = []
    print(regIDs)
    if(request.method == 'POST'):
        regId = request.POST['RegEvent']
        strs = regId.split(':')
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2}
        strs = regId.split(':')
        dept = deptDict[strs[0]]
        ayear = int(strs[3])
        asem = int(strs[4])
        myear = rom2int[strs[1]]
        msem = rom2int[strs[2]]
        regulation = int(strs[5])
        mode = strs[6]
        currentRegEventId = MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
        currentRegEventId = currentRegEventId[0].id
        con = {} 
        if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
            con['RegEvent']=request.POST['RegEvent']
            if 'RegNo' in request.POST.keys():
                con['RegNo']=request.POST['RegNo']
            form = BacklogRegistrationForm(regIDs, con)
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
            form = BacklogRegistrationForm(regIDs, request.POST)
        if not 'RegNo' in request.POST.keys():
            pass 
        elif not 'Submit' in request.POST.keys():
            regNo = request.POST['RegNo']
            event = (request.POST['RegEvent'])
            studentInfo = MTStudentInfo.objects.filter(RegNo=regNo)
        elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
            regNo = request.POST['RegNo']
            event = request.POST['RegEvent']
            studentInfo = MTStudentInfo.objects.filter(RegNo=regNo) 
            # studyModeCredits = 0
            # examModeCredits = 0
            # for sub in form.myFields:
            #     if(form.cleaned_data['Check'+str(sub[9])]):
            #         if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
            #             if(form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
            #                 studyModeCredits += sub[2]
            #             else:
            #                 examModeCredits += sub[2]
            #         else:
            #             form = BacklogRegistrationForm(request.POST)
            #             context = {'form':form, 'msg': 2}  
            #             if(len(studentInfo)!=0):
            #                 context['RegNo'] = studentInfo[0].RegNo
            #                 context['Name'] = studentInfo[0].Name  
            #             return render(request, 'MTco_ordinator/BTBacklogRegistration.html',context)

            # if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
            for sub in form.myFields:
                    # if(sub[6]=='R'): #Handling Regular Subjects
                        # regular_sub = MTSubjects.objects.get(id=sub[9])
                        # for regular and dropped there is no need to check if it is selected!!!
                        # if form.cleaned_data['Check'+str(sub[9])] == False:   #delete regular_record from the registration table
                        #     reg = MTStudentRegistrations_Staging.objects.\
                        #         filter(RegNo = request.POST['RegNo'], RegEventId=regular_sub.RegEventId,sub_id = sub[9], id=sub[10])
                        #     if len(reg) != 0:
                        #         MTStudentRegistrations_Staging.objects.get(RegNo = request.POST['RegNo'], RegEventId=regular_sub.RegEventId,\
                        #              sub_id = sub[9], id=sub[10]).delete()
                        #         new_dropped_course = DroppedRegularCourses(RegNo=request.POST['RegNo'], sub_id=sub[9])
                        #         new_dropped_course.save()
                    # elif sub[6] == 'D':
                    #     if form.cleaned_data['Check'+str(sub[9])] == False:
                    #         MTStudentRegistrations_Staging.objects.filter(RegNo = request.POST['RegNo'], sub_id = sub[9], \
                    #             id=sub[10]).delete()
                    # else:   #Handling Backlog Subjects
                    if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
                        #update operation mode could be study mode or exam mode
                        MTStudentRegistrations_Staging.objects.filter(id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+str(sub[9])])
                    elif(sub[5]):
                        #delete record from registration table
                        MTStudentRegistrations_Staging.objects.filter(id=sub[10]).delete()
                    elif(form.cleaned_data['Check'+str(sub[9])]):
                        #insert backlog registration
                        if sub[10]=='':
                            newRegistration = MTStudentRegistrations_Staging(RegNo = request.POST['RegNo'],RegEventId=currentRegEventId,\
                            Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
                            newRegistration.save()     
                    return(render(request,'MTco_ordinator/BTBacklogRegistrationSuccess.html'))

            # else:
            #     form = BacklogRegistrationForm(request.POST)
            #     context = {'form':form, 'msg':1}
            #     context['study']=studyModeCredits
            #     context['exam']=examModeCredits
            #     if(len(studentInfo)!=0):
            #         context['RegNo'] = studentInfo[0].RegNo
            #         context['Name'] = studentInfo[0].Name  
            #     return render(request, 'SupExamDBRegistrations/BTBacklogRegistration.html',context)
        # else:
        #     print("form validation failed")             
    else:
        form = BacklogRegistrationForm(regIDs)
    context = {'form':form, 'msg':0}
    if(len(studentInfo)!=0):
        context['RegNo'] = studentInfo[0].RegNo
        context['Name'] = studentInfo[0].Name  
    return render(request, 'MTco_ordinator/BTBacklogRegistration.html',context)
