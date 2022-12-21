from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from ADAUGDB.user_access_test import is_Associate_Dean_Academics
from BTco_ordinator.forms import OpenElectiveRegistrationsForm
from BTco_ordinator.models import BTStudentRegistrations, BTSubjects, BTStudentRegistrations_Staging,BTRollLists_Staging,BTRollLists
from ADAUGDB.forms import OpenElectiveRegistrationsFinalizeForm
from ADAUGDB.models import BTOpenElectiveRollLists
from ADAUGDB.models import BTRegistrationStatus
from import_export.formats.base_formats import XLSX
from django.db import transaction

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def open_elective_regs(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =None
    if 'Associate-Dean-Academics' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, OERegistrationStatus=1, Mode__in=['R','B'])
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
        
        if regId != '--Choose Event--' and subId != '--Select Subject--' :
            strs = regId.split(':')
            ayear = int(strs[2])
            asem = int(strs[3])
            byear = rom2int[strs[0]]
            bsem = rom2int[strs[1]]
            regulation = float(strs[4])
            mode = strs[5]
            
            rolls = BTOpenElectiveRollLists.objects.filter(subject_id=subId,RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode).order_by('student__id')
            BTRollLists_Staging.objects.filter()

            for i in range(len(rolls)):
                reg = BTStudentRegistrations_Staging(student=rolls[i].student, RegEventId=rolls[i].RegEventId, Mode=1,sub_id=subId)
                reg.save()
            return render(request, 'ADAUGDB/OecRegistrationsSuccess.html')
        elif regId != '--Choose Event--':
            strs = regId.split(':')
            ayear = int(strs[2])
            asem = int(strs[3])
            byear = rom2int[strs[0]]
            bsem = rom2int[strs[1]]
            regulation = float(strs[4])
            mode = strs[5]
            subjects = BTSubjects.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,\
            RegEventId__BYear=byear,RegEventId__BSem=asem,RegEventId__Regulation=regulation,RegEventId__Mode=mode,\
                RegEventId__Status=1, RegEventId__OERollListStatus=1, course__CourseStructure__Category__in=['OEC', 'OPC'])
            subjects = [(sub.id,str(sub.course.SubCode)+" "+str(sub.course.SubName)) for sub in subjects]
            form = OpenElectiveRegistrationsForm(regIDs,subjects,data)
    else:
        form = OpenElectiveRegistrationsForm(regIDs)
    return render(request, 'ADAUGDB/OpenElectiveRegistrations.html',{'form':form,'msg':necessary_field_msg})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(is_Associate_Dean_Academics)
def open_elective_regs_finalize(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs =  []
    msg = ''
    if 'Associate-Dean-Academics' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, OERegistrationStatus=1, Mode__in=['R','B'])
    if regIDs:
        regIDs = [(row.AYear, row.ASem, row.BYear, row.BSem, row.Dept, row.Mode, row.Regulation) for row in regIDs]
    if request.method == 'POST':
        form = OpenElectiveRegistrationsFinalizeForm(regIDs, request.POST)
        if form.is_valid():
            rom2int = {'I':1,'II':2,'III':3,'IV':4}
            regid = form.cleaned_data.get('redID')
            strs = regid.split(':')
            ayear = int(strs[2])
            asem = int(strs[3])
            byear = rom2int[strs[0]]
            bsem = rom2int[strs[1]]
            regulation = float(strs[4])
            mode = strs[5]
            rolls = BTRollLists.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode)
            staging_regs = BTStudentRegistrations_Staging.objects.filter(RegEventId__AYear=ayear,RegEventId__ASem=asem,RegEventId__BYear=byear,RegEventId__BSem=bsem,RegEventId__Regulation=regulation,RegEventId__Mode=mode)
            for reg in staging_regs:
                roll = rolls.filter(student=reg.student.student).first()
                final_reg = BTStudentRegistrations(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                final_reg.save()
            BTRegistrationStatus.objects.filter(AYear=ayear,BYear=byear,ASem=asem,BSem=bsem,Regulation=regulation,Mode=mode).update(OERegistartionStatus=0)


                
            msg = 'Open elective registrations are finalized.'
        return render(request, 'ADAUGDB/OpenElectiveRegistrationsFinalize.html', {'form':form, 'msg':msg})
    else:
        form = OpenElectiveRegistrationsFinalizeForm(regIDs)
    return render(request, 'ADAUGDB/OpenElectiveRegistrationsFinalize.html', {'form':form})