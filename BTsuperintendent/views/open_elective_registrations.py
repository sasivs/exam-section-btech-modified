from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTsuperintendent.user_access_test import is_Superintendent
from BTco_ordinator.forms import OpenElectiveRegistrationsForm
from BTco_ordinator.models import BTStudentRegistrations, BTSubjects, BTStudentRegistrations_Staging
from BTsuperintendent.forms import OpenElectiveRegistrationsFinalizeForm
from ADUGDB.models import BTRegistrationStatus
from import_export.formats.base_formats import XLSX

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def open_elective_regs(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Superintendent' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, OERegistrationStatus=1, Mode='R')
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    necessary_field_msg = False
    subjects=[]
    if(request.method == "POST"):
        depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
        years = {1:'I',2:'II',3:'III',4:'IV'}
        deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
        rom2int = {'I':1,'II':2,'III':3,'IV':4}
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
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            for i in range(len(dataset)):
                regNo = int(dataset[i][0])
                reg = BTStudentRegistrations_Staging(student__student__RegNo=regNo, RegEventId=currentRegEventId, Mode=1,sub_id=subId)
                reg.save()
            return render(request, 'BTsuperintendent/OecRegistrationsSuccess.html')
        elif regId != '--Choose Event--':
            strs = regId.split(':')
            dept = deptDict[strs[0]]
            ayear = int(strs[3])
            asem = int(strs[4])
            byear = rom2int[strs[1]]
            bsem = rom2int[strs[2]]
            regulation = int(strs[5])
            mode = strs[6]
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
                    Dept=dept,Mode=mode,Regulation=regulation)
            currentRegEventId = currentRegEventId[0].id
            subjects = BTSubjects.objects.filter(RegEventId=currentRegEventId, Category__in=['OEC','OPC'])
            subjects = [(sub.id,str(sub.SubCode)+" "+str(sub.SubName)) for sub in subjects]
            form = OpenElectiveRegistrationsForm(regIDs,subjects,data)
    else:
        form = OpenElectiveRegistrationsForm(regIDs)
    return render(request, 'BTsuperintendent/OpenElectiveRegistrations.html',{'form':form,'msg':necessary_field_msg})

@login_required(login_url="/login/")
@user_passes_test(is_Superintendent)
def open_elective_regs_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =  []
    msg = ''
    if 'Superintendent' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, OERegistrationStatus=1, Mode='R')
    if request.method == 'POST':
        form = OpenElectiveRegistrationsFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            staging_regs = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=form.cleaned_data.get('regID'), sub_id_id=form.cleaned_data.get('sub'))
            for reg in staging_regs:
                final_reg = BTStudentRegistrations(RegNo=reg.RegNo, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                final_reg.save()
            msg = 'Open elective registrations are finalized.'
        return render(request, 'BTsuperintendent/OpenElectiveRegistrationsFinalize.html', {'form':form, 'msg':msg})
    else:
        form = OpenElectiveRegistrationsFinalizeForm(regIDs)
    return render(request, 'BTsuperintendent/OpenElectiveRegistrationsFinalize.html', {'form':form})