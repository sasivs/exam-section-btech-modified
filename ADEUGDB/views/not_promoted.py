from django.contrib.auth.decorators import login_required, user_passes_test
from BThod.models import BTCoordinator 
from ADAUGDB.user_access_test import not_promoted_access, not_promoted_status_access
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ADEUGDB.forms import NotPromotedListForm, NotPromotedUploadForm, NotPromotedUpdateForm, NotPromotedStatusForm
from BTco_ordinator.models import BTNotRegistered, BTStudentGradePoints, BTNotPromoted, BTRollLists, BTStudentBacklogs, BTDroppedRegularCourses, BTStudentRegistrations,\
    BTNPRDroppedRegularCourses, BTNPRMarks, BTNPRNotRegistered, BTNPRRollLists, BTNPRStudentGrades, BTNPRStudentRegistrations, BTRollLists_Staging, BTStudentRegistrations_Staging,\
        BTSubjects
from ADAUGDB.models import BTRegistrationStatus, BTCycleCoordinator, BTHOD
from BTfaculty.models import BTStudentGrades, BTMarks, BTMarks_Staging, BTStudentGrades_Staging
from BTExamStaffDB.models import BTStudentInfo
from ADEUGDB.models import BTYearMandatoryCredits
from BTco_ordinator.resources import NotPromotedResource
from django.db.models import Q
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from django.http.response import HttpResponse
from django.db import transaction
# Import render module


'''
Utility function for sorting
'''

def get_regd_no(np):
    return np.get('student').RegNo

@login_required(login_url="/login/")
@user_passes_test(not_promoted_access)
def not_promoted_list(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=1, Dept=cycle_cord.Cycle, Mode='R')
    elif 'Associate-Dean-Exams' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
    if request.method == 'POST':
        form = NotPromotedListForm(regIDs, request.POST)
        if form.is_valid():
            event = form.cleaned_data['RegEvent']
            strs = event.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4} 
            dept = deptDict[strs[0]]
            ayear =int(strs[2])
            byear = rom2int[strs[1]]
            regulation = float(strs[3])
            currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,BYear=byear,Dept=dept,Regulation=regulation, Mode='R')
            rolls = BTRollLists.objects.filter(RegEventId__in=currentRegEventId).distinct('student__RegNo')
            
            not_promoted_b_mode = BTNotPromoted.objects.filter(AYear=ayear-1, BYear=byear, Regulation=regulation, PoA_sem1='B', PoA_sem2='B')
            mandatory_credits = BTYearMandatoryCredits.objects.filter(Regulation=regulation, BYear=byear, Dept=dept).first()
            mandatory_credits = mandatory_credits.Credits
            check_rolls = [roll for roll in rolls] + [roll for roll in not_promoted_b_mode]
            np = []
            for roll in check_rolls:
                grades = BTStudentGradePoints.objects.filter(RegNo=roll.student.RegNo, AYear=ayear, BYear=byear).filter(~Q(Grade='F')).\
                    filter(~Q(Grade='I')).filter(~Q(Grade='X')).filter(~Q(Grade='R'))
                credits=0
                for g in grades:
                    credits += g.Curriculum_Credits
                if credits < mandatory_credits:
                    d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA_sem1':'R', 'PoA_sem2':'R'}
                    np.append(d)
                else:
                    if byear == 2 or byear == 3:
                        backlogs = BTStudentBacklogs.objects.filter(RegNo=roll.student.RegNo, BYear=byear-1)
                        if len(backlogs) != 0:
                            d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA_sem1':'B', 'PoA_sem2':'B'}
                            np.append(d)
                        else:
                            dropped_courses = BTDroppedRegularCourses.objects.filter(student__RegNo=roll.student.RegNo, Registered=False, subject__RegEventId__BYear=byear-1)
                            # for course in dropped_courses:
                            #     sub = BTSubjects.objects.get(id=course.sub_id)
                            #     offeredEvent = BTRegistrationStatus.objects.get(id=sub.RegEventId)
                            #     if offeredEvent.BYear == byear-1:
                            #         check_registration = BTStudentRegistrations.objects.filter(student__student__RegNo=roll.student.RegNo, sub_id=course.sub_id)
                            #         if len(check_registration) == 0:
                            #             d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'B'}
                            #             np.append(d)
                            if dropped_courses:
                                d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA_sem1':'B', 'PoA_sem2':'B'}
                                np.append(d)
                            # elif not BTRegulationChange.objects.filter(student__RegNo=roll.student.RegNo).exists():
                            #     regEvent = BTStudentRegistrations.objects.filter(student__student__RegNo=roll.student.RegNo, RegEventId__BYear=byear-1, RegEventId__Mode='R').order_by('RegEventId__AYear').first()
                            #     subjects = BTSubjects.objects.filter(RegEventId_id=regEvent.RegEventId.id)
                            #     oec_subjects = 

                    elif byear == 4:
                        backlogs = BTStudentBacklogs.objects.filter(RegNo=roll.student.RegNo)
                        if len(backlogs) != 0:
                            d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA_sem1':'B', 'PoA_sem2':'B'}
                            np.append(d)
                        else:
                            dropped_courses = BTDroppedRegularCourses.objects.filter(student__RegNo=roll.student.RegNo, Registered=False)
                            # for course in dropped_courses:
                            #     sub = BTSubjects.objects.get(id=course.sub_id)
                            #     check_registration = BTStudentRegistrations.objects.filter(student__student__RegNo=roll.student.RegNo, sub_id=course.sub_id)
                            #     if len(check_registration) == 0:
                            #         d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA':'B'}
                            #         np.append(d)
                            if dropped_courses:
                                d = {'student':roll.student, 'AYear':ayear, 'BYear':byear, 'Regulation':regulation, 'PoA_sem1':'B', 'PoA_sem2':'B'}
                                np.append(d)
            np.sort(key=get_regd_no)
            if request.POST.get('download'):
                from BTco_ordinator.utils import NotPromotedBookGenerator
                response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                response['Content-Disposition'] = 'attachment; filename=NotPromoted({regevent}).xlsx'.format(regevent=event)
                BookGenerator = NotPromotedBookGenerator(np, regulation, event)
                workbook = BookGenerator.generate_workbook()
                workbook.save(response)
                return response
            return render(request, 'ADEUGDB/NotPromotedList.html', {'form':form, 'notPromoted':np})
    else:
        form = NotPromotedListForm(regIDs)
    return render(request, 'ADEUGDB/NotPromotedList.html', {'form':form})


@login_required(login_url="/login/")
@user_passes_test(not_promoted_access)
def not_promoted_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=coordinator.BYear, Dept=coordinator.Dept, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, BYear=1, Dept=cycle_cord.Cycle, Mode='R')
    elif 'Associate-Dean-Exams' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
    if request.method == 'POST':
        form = NotPromotedUploadForm(regIDs, request.POST, request.FILES)
        if form.is_valid() and form.cleaned_data['RegEvent']!='-- Select Registration Event --':
            regEvent = form.cleaned_data['RegEvent']
            strs = regEvent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4} 
            dept = deptDict[strs[0]]
            ayear =int(strs[2])
            byear = rom2int[strs[1]]
            regulation = float(strs[3])
            file = form.cleaned_data['file']
            data = bytes()
            for chunk in file.chunks():
                data += chunk
            dataset = XLSX().create_dataset(data)
            newDataset= Dataset()
            newDataset.headers =['student', 'AYear', 'BYear', 'Regulation','PoA_sem1', 'PoA_sem2']
            errorDataset = Dataset()
            errorDataset.headers=['student_id', 'RegNo', 'RollNo', 'Name', 'AYear', 'BYear', 'Regulation', 'PoA_sem1', 'PoA_sem2']
            for i in range(len(dataset)):
                row = dataset[i]
                if row[2] == ayear and row[3] == byear and row[4] == regulation:
                    newRow = (row[0],row[4],row[5], row[6], row[7], row[8])
                    newDataset.append(newRow)
                else:
                    newRow = (row[0],row[1],row[2],row[3],row[4],row[5], row[6], row[7], row[8])
                    errorDataset.append(newRow)
            not_promoted_resource = NotPromotedResource()
            result = not_promoted_resource.import_data(newDataset, dry_run=True)
            if not result.has_errors():
                not_promoted_resource.import_data(newDataset, dry_run=False)
                for row in newDataset:
                    student_obj = BTStudentInfo.objects.filter(id=row[0]).first()
                    if row[4] == 'R':
                        regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1]).first().RegEventId
                        regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                        rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1])
                        total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                        grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                        marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                        not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=1, RegEventId__BYear=row[2], RegEventId__AYear__lte=row[1])
                        dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                        for i in rolls:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRRollLists.objects.create(**i_dict)
                        for i in not_registered:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRNotRegistered.objects.create(**i_dict)
                        for i in total_regs:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRStudentRegistrations.objects.create(**i_dict)
                        for i in dropped_regular:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRDroppedRegularCourses.objects.create(**i_dict)
                        for i in marks:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRMarks.objects.create(**i_dict)
                        for i in grades:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            i_dict['RegId'] = i_dict['RegId_id']
                            i_dict.pop('RegId_id')
                            BTNPRStudentGrades.objects.create(**i_dict)
                        BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1]).delete()
                        # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                        BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                        BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()                        
                        rolls.delete()
                        total_regs.delete()
                        marks.delete()
                        grades.delete()
                        not_registered.delete()
                        dropped_regular.delete()
                    if row[5] == 'R':
                        regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=row[2], RegEventId__BSem=2, RegEventId__AYear__lte=row[1]).first().RegEventId
                        regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                        rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=2, RegEventId__AYear__lte=row[1])
                        total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                        grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                        marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                        not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=2, RegEventId__BYear=row[2], RegEventId__AYear__lte=row[1])
                        dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                        for i in rolls:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRRollLists.objects.create(**i_dict)
                        for i in not_registered:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRNotRegistered.objects.create(**i_dict)
                        for i in total_regs:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRStudentRegistrations.objects.create(**i_dict)
                        for i in dropped_regular:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRDroppedRegularCourses.objects.create(**i_dict)
                        for i in marks:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRMarks.objects.create(**i_dict)
                        for i in grades:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            i_dict['RegId'] = i_dict['RegId_id']
                            i_dict.pop('RegId_id')
                            BTNPRStudentGrades.objects.create(**i_dict)
                        BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1]).delete()
                        # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                        BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                        BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()
                        rolls.delete()
                        total_regs.delete()
                        marks.delete()
                        grades.delete()
                        not_registered.delete()
                        dropped_regular.delete()
                if (len(errorDataset)!=0):
                    npErrRows = [(errorDataset[i][0],errorDataset[i][1],errorDataset[i][2],errorDataset[i][3], errorDataset[i][4], errorDataset[i][5], errorDataset[i][6], errorDataset[i][7], errorDataset[i][8]) for i in range(len(errorDataset))]
                    request.session['npErrRows'] = npErrRows
                    request.session['RegEvent'] = regEvent
                    return redirect('BTNotPromotedUploadErrorHandler' )
                return(render(request,'ADEUGDB/NotPromotedUploadSuccess.html'))
            else:
                errors = result.row_errors()
                indices = set([i for i in range(len(newDataset))])    
                errorIndices = set([i[0]-1 for i in errors])
                cleanIndices = indices.difference(errorIndices)
                cleanDataset = Dataset()
                for i in list(cleanIndices):
                    cleanDataset.append(newDataset[i])
                cleanDataset.headers = newDataset.headers
                
                result1 = not_promoted_resource.import_data(cleanDataset, dry_run=True)
                if not result1.has_errors():
                    not_promoted_resource.import_data(cleanDataset, dry_run=False)
                    for row in cleanDataset:
                        student_obj = BTStudentInfo.objects.filter(id=row[0]).first()
                        if row[4] == 'R':
                            regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1]).first().RegEventId
                            regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                            rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1])
                            total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                            grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                            marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                            not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=1, RegEventId__BYear=row[2], RegEventId__AYear__lte=row[1])
                            dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                            for i in rolls:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRRollLists.objects.create(**i_dict)
                            for i in not_registered:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRNotRegistered.objects.create(**i_dict)
                            for i in total_regs:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRStudentRegistrations.objects.create(**i_dict)
                            for i in dropped_regular:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRDroppedRegularCourses.objects.create(**i_dict)
                            for i in marks:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRMarks.objects.create(**i_dict)
                            for i in grades:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                i_dict['RegId'] = i_dict['RegId_id']
                                i_dict.pop('RegId_id')
                                BTNPRStudentGrades.objects.create(**i_dict)
                            BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1]).delete()
                            # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                            BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                            BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()                        
                            rolls.delete()
                            total_regs.delete()
                            marks.delete()
                            grades.delete()
                            not_registered.delete()
                            dropped_regular.delete()
                        if row[5] == 'R':
                            regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=row[2], RegEventId__BSem=2, RegEventId__AYear__lte=row[1]).first().RegEventId
                            regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                            rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=2, RegEventId__AYear__lte=row[1])
                            total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                            grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                            marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                            not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=2, RegEventId__BYear=row[2], RegEventId__AYear__lte=row[1])
                            dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                            for i in rolls:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRRollLists.objects.create(**i_dict)
                            for i in not_registered:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRNotRegistered.objects.create(**i_dict)
                            for i in total_regs:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRStudentRegistrations.objects.create(**i_dict)
                            for i in dropped_regular:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRDroppedRegularCourses.objects.create(**i_dict)
                            for i in marks:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                BTNPRMarks.objects.create(**i_dict)
                            for i in grades:
                                i_dict = i.__dict__
                                i_dict.pop('_state')
                                i_dict['RegId'] = i_dict['RegId_id']
                                i_dict.pop('RegId_id')
                                BTNPRStudentGrades.objects.create(**i_dict)
                            BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[2], RegEventId__BSem=1, RegEventId__AYear__lte=row[1]).delete()
                            # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                            BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                            BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()
                            rolls.delete()
                            total_regs.delete()
                            marks.delete()
                            grades.delete()
                            not_registered.delete()
                            dropped_regular.delete()
                else:
                        print('Something went wrong in plain import')
                errorData = Dataset()
                for i in list(errorIndices):
                    newRow = (newDataset[i][0],dataset[i][1],dataset[i][2],dataset[i][3],newDataset[i][1],newDataset[i][2],newDataset[i][3], newDataset[i][4], newDataset[i][5])
                    errorData.append(newRow)
                for i in errorDataset:
                    errorData.append(i)
                npErrRows = [(errorData[i][0],errorData[i][1],errorData[i][2],errorData[i][3], errorData[i][4], errorData[i][5], errorData[i][6], errorData[i][7], errorDataset[i][8]) for i in range(len(errorData))]
                request.session['npErrRows'] = npErrRows
                request.session['RegEvent'] = regEvent
                return redirect('BTNotPromotedUploadErrorHandler')
    else:
        form = NotPromotedUploadForm(regIDs)
    return render(request, 'ADEUGDB/NotPromotedUpload.html', {'form':form})

@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(not_promoted_access)
def not_promoted_upload_error_handler(request):
    npErrRows = request.session.get('npErrRows')
    regEvent = request.session.get('RegEvent')
    if(request.method=='POST'):
        form = NotPromotedUpdateForm(npErrRows,request.POST)
        if(form.is_valid()):
            for cIndex, row in enumerate(npErrRows):
                if(form.cleaned_data.get('Check'+str(row[0]))):
                    BTNotPromoted.objects.filter(student_id=row[0],AYear=row[4], BYear=row[5], Regulation=row[6]).update(PoA_sem1=row[7], PoA_sem2=row[8])
                    student_obj = BTStudentInfo.objects.filter(id=row[0]).first()
                    if row[7] == 'R':
                        regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=row[5], RegEventId__BSem=1, RegEventId__AYear__lte=row[4]).first().RegEventId
                        regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                        rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[5], RegEventId__BSem=1, RegEventId__AYear__lte=row[4])
                        total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                        grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                        marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                        not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=1, RegEventId__BYear=row[5], RegEventId__AYear__lte=row[4])
                        dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                        for i in rolls:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRRollLists.objects.create(**i_dict)
                        for i in not_registered:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRNotRegistered.objects.create(**i_dict)
                        for i in total_regs:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRStudentRegistrations.objects.create(**i_dict)
                        for i in dropped_regular:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRDroppedRegularCourses.objects.create(**i_dict)
                        for i in marks:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRMarks.objects.create(**i_dict)
                        for i in grades:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            i_dict['RegId'] = i_dict['RegId_id']
                            i_dict.pop('RegId_id')
                            BTNPRStudentGrades.objects.create(**i_dict)
                        BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[5], RegEventId__BSem=1, RegEventId__AYear__lte=row[4]).delete()
                        # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                        BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                        BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()                        
                        rolls.delete()
                        total_regs.delete()
                        marks.delete()
                        grades.delete()
                        not_registered.delete()
                        dropped_regular.delete()
                    if row[8] == 'R':
                        regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=row[5], RegEventId__BSem=2, RegEventId__AYear__lte=row[4]).first().RegEventId
                        regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                        rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[5], RegEventId__BSem=2, RegEventId__AYear__lte=row[4])
                        total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                        grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                        marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                        not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=2, RegEventId__BYear=row[5], RegEventId__AYear__lte=row[4])
                        dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                        for i in rolls:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRRollLists.objects.create(**i_dict)
                        for i in not_registered:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRNotRegistered.objects.create(**i_dict)
                        for i in total_regs:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRStudentRegistrations.objects.create(**i_dict)
                        for i in dropped_regular:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRDroppedRegularCourses.objects.create(**i_dict)
                        for i in marks:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            BTNPRMarks.objects.create(**i_dict)
                        for i in grades:
                            i_dict = i.__dict__
                            i_dict.pop('_state')
                            i_dict['RegId'] = i_dict['RegId_id']
                            i_dict.pop('RegId_id')
                            BTNPRStudentGrades.objects.create(**i_dict)
                        BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=row[5], RegEventId__BSem=1, RegEventId__AYear__lte=row[4]).delete()
                        # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                        BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                        BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()
                        rolls.delete()
                        total_regs.delete()
                        marks.delete()
                        grades.delete()
                        not_registered.delete()
                        dropped_regular.delete()
            return render(request, 'ADEUGDB/NotPromotedUploadSuccess.html')
    else:
        form = NotPromotedUpdateForm(Options=npErrRows)
    return(render(request, 'ADEUGDB/NotPromotedUploadErrorHandler.html',{'form':form}))

@login_required(login_url="/login/")
@user_passes_test(not_promoted_status_access)
def not_promoted_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    regIDs = None
    if 'Superintendent' in groups or 'Associate-Dean-Academics' in groups or 'Associate-Dean-Exams' in groups:
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Mode='R')
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=hod.Dept, Mode='R')
    elif 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=coordinator.Dept, BYear=coordinator.BYear, Mode='R')
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, Dept=cycle_cord.Cycle, BYear=1, Mode='R')
    if(request.method=='POST'):
        form = NotPromotedStatusForm(regIDs, request.POST)
        if(request.POST['RegEvent']!='-- Select Registration Event --'):
            regEvent = request.POST['RegEvent']
            strs = regEvent.split(':')
            depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
            years = {1:'I',2:'II',3:'III',4:'IV'}
            deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
            rom2int = {'I':1,'II':2,'III':3,'IV':4} 
            dept = deptDict[strs[0]]
            ayear =int(strs[2])
            byear = rom2int[strs[1]]
            regulation = float(strs[3])
            if byear == 1:
                notPromoted = BTNotPromoted.objects.filter(AYear=ayear, BYear=byear, Regulation=regulation, student__Cycle=dept).order_by('student__RegNo')
            else:
                notPromoted = BTNotPromoted.objects.filter(AYear=ayear, BYear=byear, Regulation=regulation).order_by('student__RegNo')
            return render(request, 'ADEUGDB/NotPromotedStatus.html', {'notPromoted':notPromoted, 'form':form})
    else:
        form = NotPromotedStatusForm(regIDs)
    return render(request, 'ADEUGDB/NotPromotedStatus.html', {'form':form})


def not_promoted_cleansing_script():
    not_prom = BTNotPromoted.objects.all()
    for np in not_prom:
        with transaction.atomic():
            student_obj = np.student
            if np.PoA_sem1 == 'R':
                regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=np.BYear, RegEventId__BSem=1, RegEventId__AYear__lte=np.AYear).first().RegEventId
                regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=np.BYear, RegEventId__BSem=1, RegEventId__AYear__lte=np.AYear)
                total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=1, RegEventId__BYear=np.BYear, RegEventId__AYear__lte=np.AYear)
                dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRRollLists.objects.create(**i_dict)
                for i in not_registered:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRNotRegistered.objects.create(**i_dict)
                for i in total_regs:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRStudentRegistrations.objects.create(**i_dict)
                for i in dropped_regular:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRDroppedRegularCourses.objects.create(**i_dict)
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRMarks.objects.create(**i_dict)
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    i_dict['RegId'] = i_dict['RegId_id']
                    i_dict.pop('RegId_id')
                    BTNPRStudentGrades.objects.create(**i_dict)
                BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=np.BYear, RegEventId__BSem=1, RegEventId__AYear__lte=np.AYear).delete()
                # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()
                rolls.delete()
                total_regs.delete()
                marks.delete()
                grades.delete()
                not_registered.delete()
                dropped_regular.delete()
            if np.PoA_sem2 == 'R':
                regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=np.BYear, RegEventId__BSem=2, RegEventId__AYear__lte=np.AYear).first().RegEventId
                regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                rolls = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=np.BYear, RegEventId__BSem=2, RegEventId__AYear__lte=np.AYear)
                total_regs = BTStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                grades = BTStudentGrades.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True))
                marks = BTMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                not_registered = BTNotRegistered.objects.filter(Student__RegNo=student_obj.RegNo, RegEventId__BSem=2, RegEventId__BYear=np.BYear, RegEventId__AYear__lte=np.AYear)
                dropped_regular = BTDroppedRegularCourses.objects.filter(student__RegNo=student_obj.RegNo, subject_id__in=regular_subjects.values_list('id', flat=True))
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRRollLists.objects.create(**i_dict)
                for i in not_registered:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRNotRegistered.objects.create(**i_dict)
                for i in total_regs:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRStudentRegistrations.objects.create(**i_dict)
                for i in dropped_regular:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRDroppedRegularCourses.objects.create(**i_dict)
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNPRMarks.objects.create(**i_dict)
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    i_dict['RegId'] = i_dict['RegId_id']
                    i_dict.pop('RegId_id')
                    BTNPRStudentGrades.objects.create(**i_dict)
                BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BYear=np.BYear, RegEventId__BSem=1, RegEventId__AYear__lte=np.AYear).delete()
                # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()
                rolls.delete()
                total_regs.delete()
                marks.delete()
                grades.delete()
                not_registered.delete()
                dropped_regular.delete()
        return "Completed!!!"

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def not_promoted_backlog_mode_regs(request):
#     studentInfo = []
#     if(request.method == 'POST'):
#         regId = request.POST['RegEvent']
#         strs = regId.split(':')
#         depts = ['BTE','CHE','CE','CSE','EEE','ECE','ME','MME','CHEMISTRY','PHYSICS']
#         years = {1:'I',2:'II',3:'III',4:'IV'}
#         deptDict = {dept:ind+1 for ind, dept  in enumerate(depts)}
#         rom2int = {'I':1,'II':2,'III':3,'IV':4}
#         strs = regId.split(':')
#         dept = deptDict[strs[0]]
#         ayear = int(strs[3])
#         asem = int(strs[4])
#         byear = rom2int[strs[1]]
#         bsem = rom2int[strs[2]]
#         regulation = float(strs[5])
#         mode = strs[6]
#         currentRegEventId = BTRegistrationStatus.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,\
#                     Dept=dept,Mode=mode,Regulation=regulation)
#         currentRegEventId = currentRegEventId[0].id
#         con = {} 
#         if 'Submit' not in request.POST.keys() and 'RegEvent' in request.POST.keys():
#             con['RegEvent']=request.POST['RegEvent']
#             if 'RegNo' in request.POST.keys():
#                 con['RegNo']=request.POST['RegNo']
#             form = NotPromotedBacklogRegistrationForm(con)
#         elif 'RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST:
#             form = NotPromotedBacklogRegistrationForm(request.POST)
#         if not 'RegNo' in request.POST.keys():
#             pass 
#         elif not 'Submit' in request.POST.keys():
#             regNo = request.POST['RegNo']
#             event = (request.POST['RegEvent'])
#             print(regNo, event)
#             studentInfo = BTStudentInfo.objects.filter(RegNo=regNo)
#         elif('RegEvent' in request.POST and 'RegNo' in request.POST and 'Submit' in request.POST and form.is_valid()):
#             regNo = request.POST['RegNo']
#             event = (request.POST['RegEvent'])
#             studentInfo = BTStudentInfo.objects.filter(RegNo=regNo) 
#             studyModeCredits = 0
#             examModeCredits = 0
#             for sub in form.myFields:
#                 if(form.cleaned_data['Check'+str(sub[9])]):
#                     if(form.cleaned_data['RadioMode'+str(sub[9])]!=''):
#                         if(form.cleaned_data['RadioMode'+str(sub[9])]=='1'):
#                             studyModeCredits += sub[2]
#                         else:
#                             examModeCredits += sub[2]
#                     else:
#                         form = NotPromotedBacklogRegistrationForm(request.POST)
#                         context = {'form':form, 'msg': 2}  
#                         if(len(studentInfo)!=0):
#                             context['RollNo'] = studentInfo[0].RollNo
#                             context['Name'] = studentInfo[0].Name  
#                         return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)
#             if((studyModeCredits+examModeCredits<=34) and(studyModeCredits<=32)):
#                 for sub in form.myFields:
#                     if sub[6] == 'D':
#                         if form.cleaned_data['Check'+str(sub[9])] == False:
#                             BTStudentRegistrations_Staging.objects.filter(student__student__RegNo = request.POST['RegNo'], sub_id = sub[9], \
#                                 id=sub[10]).delete()
#                     else:   #Handling Backlog Subjects
#                         if((sub[5]) and (form.cleaned_data['Check'+str(sub[9])])):
#                             #update operation mode could be study mode or exam mode
#                             BTStudentRegistrations_Staging.objects.filter(student__student__RegNo = request.POST['RegNo'], \
#                                 sub_id = sub[9], id=sub[10]).update(Mode=form.cleaned_data['RadioMode'+str(sub[9])])
#                         elif(sub[5]):
#                             #delete record from registration table
#                             BTStudentRegistrations_Staging.objects.filter(student__student__RegNo = request.POST['RegNo'], \
#                                 sub_id = sub[9], id=sub[10]).delete()
#                         elif(form.cleaned_data['Check'+str(sub[9])]):
#                             #insert backlog registration
#                             if sub[10]=='':
#                                 newRegistration = BTStudentRegistrations_Staging(student__student__RegNo = request.POST['RegNo'],RegEventId=currentRegEventId,\
#                                 Mode=form.cleaned_data['RadioMode'+str(sub[9])],sub_id=sub[9])
#                                 newRegistration.save()                   
#                 return(render(request,'BTco_ordinator/BTBacklogRegistrationSuccess.html'))
#             else:
#                 form = NotPromotedBacklogRegistrationForm(request.POST)
#                 context = {'form':form, 'msg':1}
#                 context['study']=studyModeCredits
#                 context['exam']=examModeCredits
#                 if(len(studentInfo)!=0):
#                     context['RollNo'] = studentInfo[0].RollNo
#                     context['Name'] = studentInfo[0].Name  
#                 return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)
#         else:
#             print("form validation failed")   
#             print(form.errors.as_data())          
#     else:
#         form = NotPromotedBacklogRegistrationForm()
#     context = {'form':form, 'msg':0}
#     if(len(studentInfo)!=0):
#         context['RollNo'] = studentInfo[0].RollNo
#         context['Name'] = studentInfo[0].Name  
#     return render(request, 'BTco_ordinator/BTBacklogRegistration.html',context)
