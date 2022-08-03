
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTsuperintendent.user_access_test import registration_access
from MTco_ordinator.forms import OpenElectiveRegistrationsForm
from MTsuperintendent.models import MTRegistrationStatus
from MTco_ordinator.models import MTSubjects, MTStudentRegistrations_Staging
from import_export.formats.base_formats import XLSX
from MThod.models import MTCoordinator


@login_required(login_url="/login/")
@user_passes_test(registration_access)
def dept_elective_regs_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear,Mode='R')
    
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    necessary_field_msg = False
    subjects=[]
    if(request.method == "POST"):
        print(request.POST)
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME']
        years = {1:'I',2:'II'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2}
        regId = request.POST['regID']
        subId = request.POST['subId']
        data = {'regID':regId, 'subId':subId}
        form = OpenElectiveRegistrationsForm(regIDs,subjects,data)
        if 'file' not in request.POST.keys():
            file = request.FILES['file']   
        else:
            file = request.POST['file']
        if regId != '--Choose Event--' and subId != '--Select Subject--' and file != '':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            myear = rom2int[strs[1]]
            msem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            currentRegEventId=MTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,MYear=myear,MSem=msem,Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId=currentRegEventId[0].id
            for i in range(len(dataset)):
                regNo = int(dataset[i][0])
                reg = MTStudentRegistrations_Staging(RegNo=regNo, RegEventId=currentRegEventId,Mode=1,sub_id=subId)
                reg.save()
            return render(request, 'co_ordinator/Dec_Regs_success.html')
        elif regId != '--Choose Event--':
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
            subjects = MTSubjects.objects.filter(RegEventId=currentRegEventId, Category='DEC')
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            form = OpenElectiveRegistrationsForm(regIDs,subjects,data)
    else:
        form = OpenElectiveRegistrationsForm(regIDs)
    return render(request, 'co_ordinator/Dec_Registrations_upload.html',{'form':form,'msg':necessary_field_msg})
