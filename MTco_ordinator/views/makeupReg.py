from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from MTsuperintendent.user_access_test import registration_access
from MTco_ordinator.forms import MakeupRegistrationsForm
from MTco_ordinator.models import MTStudentRegistrations_Staging
from MTsuperintendent.models import MTRegistrationStatus
from MThod.models import MTCoordinator

@login_required(login_url="/login/")
@user_passes_test(registration_access)
def makeup_registrations(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = MTRegistrationStatus.objects.filter(Status=1, RegistrationStatus=1, Dept=coordinator.Dept, MYear=coordinator.MYear,Mode='M')
    
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.MYear, row.MSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if request.method == 'POST' and request.POST['RegEvent'] != '-- Select Registration Event --':
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
            form = MakeupRegistrationsForm(regIDs,con)
        elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
            form = MakeupRegistrationsForm(regIDs,request.POST)
        if 'RegNo' not in request.POST.keys() :
            pass
        elif request.POST['RegNo'] != '--Select Reg Number--' and 'Submit' not in request.POST.keys():
            pass
        elif request.POST['RegNo'] != '--Select Reg Number--' and 'Submit' in request.POST.keys() and form.is_valid():
            for sub in form.myFields:
                already_registered = MTStudentRegistrations_Staging.objects.filter(RegNo=request.POST['RegNo'], \
                        sub_id=sub[8], RegEventId=currentRegEventId)
                if form.cleaned_data['Check'+str(sub[8])]:
                    if len(already_registered) == 0:
                        newReg = MTStudentRegistrations_Staging(RegNo=request.POST['RegNo'], sub_id=sub[8],\
                            Mode=form.cleaned_data['RadioMode'+str(sub[8])], RegEventId=currentRegEventId)
                        newReg.save()
                else:
                    if len(already_registered) != 0:
                        MTStudentRegistrations_Staging.objects.get(id=already_registered[0].id).delete()
            return render(request, 'MTco_ordinator/MakeupRegistrationsSuccess.html')

    elif request.method == 'POST':
        form = MakeupRegistrationsForm(regIDs,request.POST)
    else:
        form = MakeupRegistrationsForm(regIDs)
    return render(request, 'MTco_ordinator/MakeupRegistrations.html', {'form':form})
