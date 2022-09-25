from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from BTsuperintendent.user_access_test import grades_threshold_event_wise_access
from BThod.models import BTCoordinator
from ADUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTCycleCoordinator, BTGradePoints
from BTco_ordinator.forms import GradesThresholdEventWise
from BTco_ordinator.models import BTFacultyAssignment
from BTfaculty.models import BTGradesThreshold
from import_export.formats.base_formats import XLSX


@login_required(login_url="/login/")
@user_passes_test(grades_threshold_event_wise_access)
def grades_threshold_event_wise(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        coordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=coordinator.Dept, BYear=coordinator.BYear)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        regIDs = BTRegistrationStatus.objects.filter(Status=1, RollListStatus=1, Dept=cycle_cord.Cycle, BYear=1)
    if request.method == 'POST':
        form = GradesThresholdEventWise(regIDs, request.POST, request.FILES)
        if form.is_valid():
            event_id = form.cleaned_data['regID']
            event_obj = BTRegistrationStatus.objects.filter(id=event_id).first()
            file = form.cleaned_data['file']
            import pandas as pd
            file = pd.read_excel(file)
            error_rows = []
            invalid_rows=[]
            for rindex, row in file.iterrows():
                if not (row[0]==event_obj.AYear and row[1]==event_obj.ASem and row[2]==event_obj.BYear and row[3]==event_obj.BSem and row[4]==event_obj.Dept\
                    and row[5]==event_obj.Regulation and row[6]==event_obj.Mode):
                    error_rows.append(row)
                    continue
                fac_assign_objs = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, RegEventId__AYear=row[0], RegEventId__ASem=row[1], RegEventId__BYear=row[2], RegEventId__BSem=row[3], \
                    RegEventId__Dept=row[4], RegEventId__Regulation=row[5], RegEventId__Mode=row[6], Subject__SubCode=row[7])
                for fac_assign_obj in fac_assign_objs:
                    study_grades = BTGradePoints.objects.filter(Regulation=fac_assign_obj.Subject.RegEventId.Regulation).exclude(Grade__in=['I', 'X', 'R','W'])
                    index = 8
                    for grade in study_grades:
                        if row[index] >= 0:
                            if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=grade, Exam_Mode=False).exists():
                                grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=grade, Threshold_Mark=row[index], Exam_Mode=False)
                                grades_threshold_row.save()
                            else:
                                BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=grade, Exam_Mode=False).update(Threshold_Mark=row[index])
                        else:
                            invalid_rows.append(row)
                        index += 1
                    
                    exam_grades = BTGradePoints.objects.filter(Regulation=fac_assign_obj.Subject.RegEventId.Regulation, Grade__in=['P','F'])
                    if fac_assign_obj.Subject.RegEventId.Regulation == 1:
                        p_threshold = 15
                        f_threshold = 0
                    else:
                        p_threshold = 17.5
                        f_threshold = 0
                    if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='P').first(), Exam_Mode=True).exists():
                        grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='P').first(), Threshold_Mark=p_threshold, Exam_Mode=True)
                        grades_threshold_row.save()
                    if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='F').first(), Exam_Mode=True).exists():
                        grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='F').first(), Threshold_Mark=f_threshold, Exam_Mode=True)
                        grades_threshold_row.save()
            return render(request, 'BTco_ordinator/GradesThresholdEventWise.html', {'form':form})
        
    else:
        form = GradesThresholdEventWise(regIDs)
    return render(request, 'BTco_ordinator/GradesThresholdEventWise.html', {'form':form})   