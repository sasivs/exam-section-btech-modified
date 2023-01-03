
from ADAUGDB.models import BTGradePoints, BTRegistrationStatus, BTCancelledDroppedRegularCourses, BTCancelledMarks, BTCancelledNotPromoted,\
    BTCancelledNotRegistered, BTCancelledRollLists, BTCancelledStudentGrades, BTCancelledStudentInfo, BTCancelledStudentRegistrations, BTOpenElectiveRollLists,\
    BTCourseStructure
from BTco_ordinator.models import BTSubjects, BTFacultyAssignment, BTStudentRegistrations, BTStudentBacklogs, BTRollLists_Staging,\
    BTStudentRegistrations_Staging, BTRollLists, BTNotRegistered, BTNotPromoted, BTDroppedRegularCourses, BTStudentMakeups,\
        BTStudentBacklogs, BTNPRRollLists, BTNPRNotRegistered, BTNPRDroppedRegularCourses, BTNPRMarks, BTNPRStudentRegistrations, BTNPRStudentGrades
from BTfaculty.models import BTAttendance_Shortage, BTGradesThreshold, BTMarks, BTMarks_Staging, BTStudentGrades_Staging,\
    BTStudentGrades
from BTExamStaffDB.models import BTFacultyInfo, BTIXGradeStudents, BTStudentInfo
import pandas as pd
from import_export.formats.base_formats import XLSX
from tablib import Dataset
from django.db.models import Q, Sum
from django.db import transaction, connection

def faculty_assignment(**kwargs):
    '''
    Dept can be given in the form of list consisting of departments.
    All the remaining arguments are not lists
    '''
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    for event in regEvents:
        if event.Mode == 'R':
            regEventId = event.id
            dept_sub = BTSubjects.objects.filter(RegEventId_id=regEventId)
            for sub in dept_sub:
                print(sub.__dict__)
                offering_dept = sub.course.OfferedBy
                if offering_dept > 10: offering_dept -= 2
                print(offering_dept)
                fac_name = 'fac'+str(offering_dept)
                print(fac_name)
                fac_id = BTFacultyInfo.objects.filter(Name=fac_name).first()
                if not BTFacultyAssignment.objects.filter(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id).exists():
                    fac_assign_obj = BTFacultyAssignment(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id)
                    fac_assign_obj.save()
        elif event.Mode == 'M' or event.Mode == 'B':
            regEventId = event.id
            student_regs = BTStudentRegistrations.objects.filter(RegEventId_id=regEventId).distinct('sub_id_id')
            subjects = BTSubjects.objects.filter(id__in=student_regs.values_list('sub_id_id', flat=True))
            for sub in subjects:
                print(sub.__dict__)
                offering_dept = sub.course.OfferedBy
                if offering_dept > 10: offering_dept -= 2
                print(offering_dept)
                fac_name = 'fac'+str(offering_dept)
                print(fac_name)
                fac_id = BTFacultyInfo.objects.filter(Name=fac_name).first()
                if not BTFacultyAssignment.objects.filter(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id).exists():
                    fac_assign_obj = BTFacultyAssignment(Subject_id=sub.id, RegEventId_id=regEventId, Faculty_id=fac_id.id, Coordinator_id=fac_id.id)
                    fac_assign_obj.save()
    return "Completed!!!!"


def add_marks(file, kwargs):
    import pandas as pd
    file = pd.read_excel(file)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
        return "No Events!!!!"
    invalid_rows=[]
    for regEvent in regEvents:
        curr_df = file[(file['AYear']==regEvent.AYear) & (file['ASem']==regEvent.ASem) & (file['BYear']==regEvent.BYear)\
            & (file['BSem']==regEvent.BSem) & (file['Dept']==regEvent.Dept) & (file['Regulation']==regEvent.Regulation) & \
            (file['Mode']==regEvent.Mode)]
        for rIndex, row in curr_df.iterrows():
            print(row)
            registration = BTStudentRegistrations.objects.filter(student__student__RegNo=row['RegNo'], RegEventId_id=regEvent.id, sub_id__course__SubCode=row['SubCode']).first()
            marks_row = BTMarks_Staging.objects.filter(Registration_id=registration.id).first()
            if not marks_row:
                subject = BTSubjects.objects.get(id=registration.sub_id.id)
                mark_distribution = subject.MarkDistribution
                BTMarks_Staging.objects.create(Registration=registration, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
                BTMarks.objects.create(Registration=registration, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
                marks_row = BTMarks_Staging.objects.filter(Registration_id=registration.id).first()
            mark_dis = registration.sub_id.course.MarkDistribution
            dis_names = mark_dis.DistributionNames.split(',')
            distributions = [dis.split('+') for dis in dis_names]
            marks_dis_list = mark_dis.Distribution.split(',')
            marks_dis_list = [dis.split('+') for dis in marks_dis_list]
            marks_string = marks_row.Marks.split(',')
            marks = [mark.split('+') for mark in marks_string]
            mark_index = 10
            for outer in range(len(distributions)):
                for inner in range(len(distributions[outer])):
                    mark_dis_limit = float(marks_dis_list[outer][inner])
                    if mark_dis_limit < float(row[mark_index]):
                        invalid_rows.append((rIndex,row, regEvent.__str__()))
                    else:
                        marks[outer][inner] = str(row[mark_index])
                    mark_index+=1
            marks = ['+'.join(mark) for mark in marks]
            marks_string = ','.join(marks)
            marks_row.Marks = marks_string
            marks_row.TotalMarks = marks_row.get_total_marks()
            marks_row.save()
    if invalid_rows:
        print(invalid_rows)
        print("These rows have marks greater than intended maximum marks")
    return "Completed!!!!"


def add_grades_threshold(file, kwargs=None):
    file = pd.read_excel(file)
    error_rows=[]
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "no kwargs"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    for event in regEvents:
        print(event.__dict__)
        curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
            & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
            (file['Mode']==event.Mode)]
        for rIndex, row in curr_df.iterrows():
            print(str(row['Dept'])+':'+row['SubCode'])
            fac_assign_objs = BTFacultyAssignment.objects.filter(RegEventId__Status=1, RegEventId__GradeStatus=1, RegEventId__AYear=row['AYear'], RegEventId__ASem=row['ASem'], RegEventId__BYear=row['BYear'], RegEventId__BSem=row['BSem'], \
                RegEventId__Dept=row['Dept'], RegEventId__Regulation=row['Regulation'], RegEventId__Mode=row['Mode'], Subject__course__SubCode=row['SubCode'])
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
                        error_rows.append((row, event.__str__()))
                    index += 1
                
                exam_grades = BTGradePoints.objects.filter(Regulation=fac_assign_obj.Subject.RegEventId.Regulation, Grade__in=['P','F'])

                if fac_assign_obj.Subject.RegEventId.Regulation == 1:
                    p_threshold = 15
                    f_threshold = 0
                else:
                    p_threshold = 17.5
                    f_threshold = 0
                if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='P').first(), Exam_Mode=True).exists():
                    grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='P').first(), Threshold_Mark=row[index], Exam_Mode=True)
                    grades_threshold_row.save()
                    index+=1
                if not BTGradesThreshold.objects.filter(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='F').first(), Exam_Mode=True).exists():
                    grades_threshold_row = BTGradesThreshold(Subject=fac_assign_obj.Subject, RegEventId=fac_assign_obj.RegEventId, Grade=exam_grades.filter(Grade='F').first(), Threshold_Mark=row[index], Exam_Mode=True)
                    grades_threshold_row.save()
    print("Errors")
    for er in error_rows:
        print('Error'+ er[0]['SubCode']+er[1])

    return "Completed!!"



def generate_grades(**kwargs):
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
            return "No Events!!!!"
    error_events=[]
    for event in regEvents:
        marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId_id=event.id)
        subject_objects = BTSubjects.objects.filter(id__in=marks_objects.values_list('Registration__sub_id_id', flat=True))
        attendance_shortage = BTAttendance_Shortage.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
        grades_objects = BTStudentGrades_Staging.objects.filter(RegId_id__in=marks_objects.values_list('Registration', flat=True))
        for att in attendance_shortage:
            if grades_objects.filter(RegId_id=att.Registration.id):
                grades_objects.filter(RegId_id=att.Registration.id).update(Grade='R', AttGrade='X')
            else:
                grade = BTStudentGrades_Staging(RegId_id=att.Registration.id, RegEventId=att.Registration.RegEventId.id, Regulation=att.Registration.RegEventId.Regulation, \
                    Grade='R', AttGrade='X') 
                grade.save()
            marks_objects = marks_objects.exclude(Registration=att.Registration)
        ix_grades = BTIXGradeStudents.objects.filter(Registration__in=marks_objects.values_list('Registration', flat=True))
        for ix_grade in ix_grades:
                if grades_objects.filter(RegId_id=ix_grade.Registration.id):
                    grades_objects.filter(RegId_id=ix_grade.Registration.id).update(Grade=ix_grade.Grade, AttGrade='P')
                else:
                    grade = BTStudentGrades_Staging(RegId_id=ix_grade.Registration.id, RegEventId=ix_grade.Registration.RegEventId.id, Regulation=ix_grade.Registration.RegEventId.Regulation, \
                        Grade=ix_grade.Grade, AttGrade='P')
                    grade.save()
                marks_objects = marks_objects.exclude(Registration=ix_grade.Registration)
        
        for mark in marks_objects:
            subject = subject_objects.filter(id=mark.Registration.sub_id.id).first()
            if mark.Registration.Mode == 1:
                thresholds = BTGradesThreshold.objects.filter(Subject_id=subject.id, RegEventId=mark.Registration.RegEventId, Exam_Mode=False).order_by('-Threshold_Mark', 'Grade_id')
            else:
                thresholds = BTGradesThreshold.objects.filter(Subject_id=subject.id, RegEventId=mark.Registration.RegEventId, Exam_Mode=True).order_by('-Threshold_Mark', 'Grade_id')
            if not thresholds:
                if BTStudentRegistrations.objects.filter(sub_id_id=subject.id, RegEventId_id=mark.Registration.RegEventId).exists():
                    error_events.append((event, subject.course.SubCode))
            if mark.Registration.Mode == 1:
                graded = False
                if event.ASem != 2 or event.AYear != 2019 or event.BYear != 4:
                    promote_thresholds = subject.course.MarkDistribution.PromoteThreshold
                    promote_thresholds = promote_thresholds.split(',')
                    promote_thresholds = [thr.split('+') for thr in promote_thresholds]
                    marks_list = mark.Marks.split(',')
                    marks_list = [m.split('+') for m in marks_list]
                    for outer_index in range(len(promote_thresholds)):
                        for inner_index in range(len(promote_thresholds[outer_index])):
                            if float(marks_list[outer_index][inner_index]) < float(promote_thresholds[outer_index][inner_index]):
                                graded = True
                                if grades_objects.filter(RegId_id=mark.Registration.id):
                                    grades_objects.filter(RegId_id=mark.Registration.id).update(Grade='F', AttGrade='P')
                                    break
                                else:
                                    grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                        Grade='F', AttGrade='P')
                                    grade.save()
                                    break
                        if graded:
                            break
                if not graded:
                    for threshold in thresholds:
                        if mark.TotalMarks >= threshold.Threshold_Mark:
                            if grades_objects.filter(RegId_id=mark.Registration.id):
                                grades_objects.filter(RegId_id=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='P')
                                break
                            else:
                                grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                    Grade=threshold.Grade.Grade, AttGrade='P')
                                grade.save()
                                break
            else:
                for threshold in thresholds:
                    if mark.TotalMarks >= threshold.Threshold_Mark:
                        if grades_objects.filter(RegId_id=mark.Registration.id):
                            grades_objects.filter(RegId_id=mark.Registration.id).update(Grade=threshold.Grade.Grade, AttGrade='X')
                            break
                        else:
                            grade = BTStudentGrades_Staging(RegId_id=mark.Registration.id, RegEventId=mark.Registration.RegEventId.id, Regulation=mark.Registration.RegEventId.Regulation, \
                                    Grade=threshold.Grade.Grade, AttGrade='X')
                            grade.save()
                            break
    print(set(error_events))

def backlog_registrations(file, kwargs=None):
    import pandas as pd
    file = pd.read_excel(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "No events"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    for event in regEvents:
        print(event.__dict__)
        curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
            & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
            (file['Mode']==event.Mode)]    
        for rIndex, row in curr_df.iterrows():
            print(row)
            if row['BYear'] == 1:
                backlogs = BTStudentBacklogs.objects.filter(RegNo=row['RegNo'], BYear=row['BYear'], Dept=row['Dept'])
            else:
                backlogs = BTStudentBacklogs.objects.filter(RegNo=row['RegNo'], BYear=row['BYear'], Dept=row['Dept'], BSem=row['BSem'])
            regEventId = BTRegistrationStatus.objects.filter(AYear=row['AYear'], ASem=row['ASem'], BYear=row['BYear'], BSem=row['BSem'], Dept=row['Dept'], Regulation=row['Regulation'], Mode=row['Mode']).first()
            subject_id = backlogs.filter(SubCode=row['SubCode']).first()
            if subject_id.Category not in ['OEC', 'OPC', 'DEC']:
                student = BTRollLists_Staging.objects.filter(student__RegNo=row['RegNo'], RegEventId_id=regEventId.id).first()
                if not BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=row['RegNo'], RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).exists():
                    registration_obj = BTStudentRegistrations_Staging(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id, Mode=row['RMode'])
                    registration_obj.save()
                else:
                    BTStudentRegistrations_Staging.objects.filter(student=student, RegEventId_id=regEventId.id, sub_id_id=subject_id.sub_id).update(Mode=row['RMode'])
    return "Completed!!"


def add_Rixgrades(file, kwargs=None):
    import pandas as pd
    file = pd.read_excel(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "no kwargs"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    error_rows=[]
    for event in regEvents:
        print(event.__dict__)
        curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
            & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
            (file['Mode']==event.Mode)]    
        for rIndex, row in curr_df.iterrows():
            print(row)
            regEvent = BTRegistrationStatus.objects.filter(AYear=row['AYear'], ASem=row['ASem'], BYear=row['BYear'], BSem=row['BSem'], Dept=row['Dept'], Regulation=row['Regulation'], Mode=row['Mode']).first()
            registration = BTStudentRegistrations.objects.filter(student__student__RegNo=row['RegNo'], RegEventId_id=regEvent.id, sub_id__course__SubCode=row['SubCode']).first()
            if registration:
                if row['Grade'] == 'R':
                    if not BTAttendance_Shortage.objects.filter(Registration_id=registration.id).exists():
                        att_short = BTAttendance_Shortage(Registration_id=registration.id)
                        att_short.save()
                else:
                    if not BTIXGradeStudents.objects.filter(Registration_id=registration.id).exists():
                        ix_grade = BTIXGradeStudents(Registration_id=registration.id, Grade=row['Grade'])
                        ix_grade.save()
                    else:
                        BTIXGradeStudents.objects.filter(Registration_id=registration.id).update(Grade=row['Grade'])
            else:
                error_rows.append((row, event.__dict__))
    print(error_rows)
    if error_rows:
        print("These rows have no registrations.")
        
    return 'Completed!!'

def roll_list_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    errors = []
    for event in events:
        BTNotRegistered.objects.filter(RegEventId_id=event.id).delete()
        if event.Mode == 'R':
            if event.BYear == 1:
                if event.ASem == 1:
                    students = BTStudentInfo.objects.filter(AdmissionYear=event.AYear,Cycle=event.Dept,Regulation=event.Regulation)
                    not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1,BYear=1, PoA_sem1='R', student__Regulation=event.Regulation, student__Cycle=event.Dept)
                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                    
                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []
                    for stu_obj in students:
                        if not BTRollLists.objects.filter(student__RegNo=stu_obj.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                    RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=stu_obj.RegNo).exists():
                                roll = BTRollLists_Staging(student=stu_obj, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(stu_obj.RegNo)
                    
                    for not_prom_obj in not_prom_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)
                    
                    for not_reg_obj in not_registered_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()

                elif event.ASem == 2:
                    previous_sem_event = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=1, BYear=event.BYear, BSem=1, Regulation=event.Regulation, Mode='R', Dept=event.Dept).first()
                    previous_sem_rolllist = BTRollLists_Staging.objects.filter(RegEventId__id=previous_sem_event.id)
                    previous_sem_not_reg_students = BTNotRegistered.objects.filter(RegEventId_id=previous_sem_event.id)

                    not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1,BYear=1, PoA_sem2='R', student__Regulation=event.Regulation, student__Cycle=event.Dept)

                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)

                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []

                    for roll in previous_sem_rolllist:
                        if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(roll.student.RegNo)
                        
                    for not_prom_obj in not_prom_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)

                    for not_reg_obj in not_registered_students|previous_sem_not_reg_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    

                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()
            
            else:
                if event.ASem == 1:
                    if event.BYear == 2:
                        prev_yr_not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear-1, Regulation=event.Regulation)
                        previous_year_rolllist = BTRollLists.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear-1, \
                            RegEventId__Regulation=event.Regulation, RegEventId__Mode=event.Mode, student__Dept=event.Dept).exclude(student__in=prev_yr_not_prom_students.values_list('student', flat=True))
                    else:
                        prev_yr_not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear-1, Regulation=event.Regulation, student__Dept=event.Dept)
                        previous_year_rolllist = BTRollLists.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear-1, \
                            RegEventId__Regulation=event.Regulation, RegEventId__Mode=event.Mode, RegEventId__Dept=event.Dept).exclude(student__in=prev_yr_not_prom_students.values_list('student', flat=True))
                    
                    not_prom_r_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, student__Regulation=event.Regulation, PoA_sem1='R')

                    not_prom_b_students = BTNotPromoted.objects.filter(AYear=event.AYear-2, BYear=event.BYear-1, student__Regulation=event.Regulation, PoA_sem1='B', PoA_sem2='B')

                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                    
                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []
                    
                    for roll in previous_year_rolllist:
                        if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                                RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id)
                                roll.save()
                            valid_regnos.append(roll.student.RegNo)
                    
                    for not_prom_obj in not_prom_r_students|not_prom_b_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)
                    
                    for not_reg_obj in not_registered_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    
                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()
                
                if event.ASem == 2:
                    previous_sem_event = BTRegistrationStatus.objects.filter(AYear=event.AYear, ASem=1, BYear=event.BYear, BSem=1, Regulation=event.Regulation, Mode='R', Dept=event.Dept).first()
                    previous_sem_rolllist = BTRollLists_Staging.objects.none()
                    previous_sem_not_reg_students = BTNotRegistered.objects.none()
                    if previous_sem_event:
                        previous_sem_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=previous_sem_event.id)
                        previous_sem_not_reg_students = BTNotRegistered.objects.filter(RegEventId_id=previous_sem_event.id)

                    not_prom_students = BTNotPromoted.objects.filter(AYear=event.AYear-1, BYear=event.BYear, PoA_sem2='R', student__Regulation=event.Regulation, student__Dept=event.Dept)

                    not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, \
                        Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
                    
                    initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
                    valid_regnos = []

                    for roll in previous_sem_rolllist:
                        if not BTRollLists.objects.filter(student__RegNo=roll.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=roll.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=roll.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(roll.student.RegNo)
                    
                    for not_prom_obj in not_prom_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_prom_obj.student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_prom_obj.student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_prom_obj.student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_prom_obj.student.RegNo)
                    
                    for not_reg_obj in not_registered_students|previous_sem_not_reg_students:
                        if not BTRollLists.objects.filter(student__RegNo=not_reg_obj.Student.RegNo, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem, RegEventId__Mode=event.Mode, \
                            RegEventId__AYear__lt=event.AYear).exists():
                            if not initial_rolllist.filter(student__RegNo=not_reg_obj.Student.RegNo).exists():
                                roll = BTRollLists_Staging(student=not_reg_obj.Student, RegEventId_id=event.id, Cycle=event.Dept)
                                roll.save()
                            valid_regnos.append(not_reg_obj.Student.RegNo)
                    
                    BTRollLists_Staging.objects.filter(~Q(student__RegNo__in=valid_regnos), RegEventId_id=event.id).delete()

        elif event.Mode == 'B':
            initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)

            backlog_students = BTStudentBacklogs.objects.filter(BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Regulation=event.Regulation).exclude(AYASBYBS__startswith=event.AYear).order_by('RegNo').distinct('RegNo')

            if event.BYear == 1:
                for student in backlog_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id, Cycle=event.Dept)
                        roll.save()
            else:
                for student in backlog_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                        roll.save()
                    
            BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__RegNo__in=backlog_students.values_list('RegNo', flat=True)).delete()

        elif event.Mode == 'M':
            initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
            
            makeup_students = BTStudentMakeups.objects.filter(Dept=event.Dept, BYear=event.BYear, BSem=event.BSem, Regulation=event.Regulation).distinct('RegNo').order_by('RegNo')

            if event.BYear == 1:
                for student in makeup_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id, Cycle=event.Dept)
                        roll.save()
            else:
                for student in makeup_students:
                    student = BTStudentInfo.objects.get(RegNo=student.RegNo)
                    if not initial_rolllist.filter(student=student).exists():
                        roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                        roll.save()
            
            BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__RegNo__in=makeup_students.values_list('RegNo', flat=True)).delete()

        elif event.Mode == 'D':
            initial_rolllist = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)

            dropped_courses_students = BTDroppedRegularCourses.objects.filter(Registered=False, subject_RegEventId__BYear=event.BYear, subject__RegEventId__Regulation=event.Regulation).\
                exclude(subject__RegEventId__AYear=event.AYear).distinct('student__RegNo').order_by('student__RegNo')

            for student in dropped_courses_students:
                if not initial_rolllist.filter(student=student).exists():
                    roll = BTRollLists_Staging(student=student, RegEventId_id=event.id)
                    roll.save()
        rollList_download_script(event)
        result = rollnoverification(event)
        if result:
            errors.append(result.__str__())
        else:
            rollList_fee_upload_script(dprefix+'RollList({event}).xlsx'.format(event=event.__str__().replace(':','_')), event.__dict__)
            # rolls_finalize_script(event.__dict__)
    print(errors)
    print("These events have errors in rolls verification(right_only)")
    return "Done"

def rollList_fee_upload_script(file, kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    file = pd.read_excel(file)
    # data = bytes()
    # for chunk in file.chunks():
    #     data += chunk
    
    event = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), ASem=kwargs.get('ASem'), BYear=kwargs.get('BYear'), BSem=kwargs.get('BSem'),\
        Regulation=kwargs.get('Regulation'), Dept=kwargs.get('Dept'), Mode=kwargs.get('Mode')).first()
    mode = event.Mode
    paid_regd_no = []
    for _,row in file.iterrows():
        paid_regd_no.append(row['RegNo'])
    rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
    unpaid_regd_no = rolls.exclude(student__RegNo__in=paid_regd_no)
    rolls = rolls.values_list('student__RegNo', flat=True)
    error_regd_no = set(paid_regd_no).difference(set(rolls))
    if mode == 'R':
        for regd_no in unpaid_regd_no:
            not_registered = BTNotRegistered(Student=regd_no.student, RegEventId_id=event.id, Registered=False)
            not_registered.save()
    unpaid_regd_no = unpaid_regd_no.values_list('student__RegNo', flat=True) 
    BTStudentRegistrations_Staging.objects.filter(student__student__RegNo__in=unpaid_regd_no, RegEventId=event.id).delete()
    BTRollLists_Staging.objects.filter(student__RegNo__in=unpaid_regd_no, RegEventId_id=event.id).delete() 
    currentRegEvent = BTRegistrationStatus.objects.get(id=event.id)
    currentRegEvent.RollListFeeStatus = 1
    currentRegEvent.save()
    print(error_regd_no)
    print('These roll numbers are not there in roll list')
    return "Done!"

def rolls_finalize_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    for event in events:
        rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
        for roll in rolls:
            if(not BTRollLists.objects.filter(student=roll.student, RegEventId=roll.RegEventId).exists()):
                finalized_roll = BTRollLists(student=roll.student, RegEventId=roll.RegEventId, Section=roll.Section, Cycle=roll.Cycle)
                finalized_roll.save()
        event.RollListStatus = 0
        event.save()
    return "Done! "

def rollList_download_script(event):
    from BTco_ordinator.utils import RollListBookGenerator

    rollListStatus=BTRollLists_Staging.objects.filter(RegEventId_id=event.id).order_by('student__RegNo')
    # print(rollListStatus.count())
    headers = ['id', 'RegNo', 'RollNo', 'Name', 'Dept', 'Cycle', 'Section']
    df = pd.DataFrame(rollListStatus.values_list('id', 'student__RegNo', 'student__RollNo', 'student__Name', 'RegEventId__Dept', 'Cycle', 'Section'), columns=headers)
    # df.columns = headers
    filename = 'RollList({event}).xlsx'.format(event=event.__str__().replace(':','_'))
    # print(dprefix+filename)
    # print(df.shape)
    # print(df.head())
    df.to_excel(dprefix+filename, index=False)
    return "Done!!"

def rollnoverification(event):
    prefix = '/home/examsection/Desktop/awsp_testing_v2/database_recreate/'
    aprefix = '/home/examsection/Desktop/Data/SectionWise/2019/'
    dprefix = '/home/examsection/Downloads/'
    roll_list_name = 'RollList({event}).xlsx'.format(event=event.__str__().replace(':','_'))
    df  = pd.read_excel(dprefix + roll_list_name)
    # dddf = pd.read_excel(dprefix + roll_list_name)
    ddf = pd.read_excel(dataPrefix + '2019-Marks-Data-4.xlsx')
    ddf = ddf[(ddf['Regulation']==event.Regulation) & (ddf['Dept']==event.Dept) & (ddf['BSem']==event.BSem)\
        &(ddf['BYear']==event.BYear) &(ddf['ASem']==event.ASem)&(ddf['AYear']==event.AYear)&(ddf['Mode']==event.Mode)].drop_duplicates(subset='RegNo')

    res =pd.merge(df.drop_duplicates(subset='RegNo'),ddf.drop_duplicates(subset='RegNo'),on='RegNo',how='outer',indicator=True)

    print(res[res['_merge']!='both'].shape)
    print(df.columns)
    print(ddf.columns)
    print(ddf.shape)
    # print(dddf.columns)

    res.to_excel(dprefix + 'SampleRes.xlsx',index=False)

    error_df = pd.read_excel(dprefix+'SampleRes.xlsx')
    error_df_right_only = error_df[error_df['_merge']=='right_only']
    if not error_df_right_only.empty:
        res.to_excel(dprefix + 'SampleRes({event}).xlsx'.format(event=event.__str__().replace(':','_')),index=False)
        return event
    error_df = error_df[error_df['_merge']=='left_only']
    for _,row in error_df.iterrows():
        df = df[df['RegNo']!=row['RegNo']]
        
    df.to_excel(dprefix+roll_list_name, index=False)

def regular_regs_script(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    result = []
    for event in events:
        if event.Mode != 'R':
            continue
        print(event.__dict__)
        not_registered_students = BTNotRegistered.objects.filter(RegEventId__AYear=event.AYear-1, RegEventId__BYear=event.BYear, RegEventId__BSem=event.BSem,\
            Student__Regulation=event.Regulation, RegEventId__Dept=event.Dept)
        mode = 1
        if(event.BYear==1):
            rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', flat=True))
            if len(rolls)==0:
                msg = 'There is no roll list for the selected registration event.'
                result.append((msg, event.__str__()))
            subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
            if len(subs)==0:
                msg = 'There are no subjects for the selected registration event.'
                result.append((msg, event.__str__()))
            initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
            for roll in rolls:
                for sub in subs:
                    if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                        regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                        regRow.save()
            BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
            msg = 'Your data upload for Student Registrations has been done successfully.'
            result.append((msg, event.__str__()))
        else:
            rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id).exclude(student__in=not_registered_students.values_list('Student', flat=True))
            if len(rolls)==0:
                msg = 'There is no roll list for the selected registration event.'
                result.append((msg, event.__str__()))
            subs = BTSubjects.objects.filter(~Q(course__CourseStructure__Category__in=['OEC', 'OPC', 'DEC']),RegEventId=event)
            if len(subs)==0:
                msg = 'There are no subjects for the selected registration event.'
                result.append((msg, event.__str__()))
            initial_registrations = BTStudentRegistrations_Staging.objects.filter(RegEventId_id=event.id, Mode=1)
            for roll in rolls:
                for sub in subs:
                    if not initial_registrations.filter(student=roll, sub_id_id=sub.id).exists():
                        regRow = BTStudentRegistrations_Staging(student=roll, Mode=mode, RegEventId_id=event.id, sub_id_id=sub.id)
                        regRow.save()
            msg = 'Your data upload for Student Registrations has been done successfully.'
            BTStudentRegistrations_Staging.objects.filter(~Q(student__student__RegNo__in=rolls.values_list('student__RegNo', flat=True)), RegEventId_id=event.id).delete()
            result.append((msg, event.__str__()))
    return result

def registrations_finalize(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    events = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'), BSem__in=kwargs.get('BSem'),\
        Regulation__in=kwargs.get('Regulation'), Dept__in=kwargs.get('Dept'), Mode__in=kwargs.get('Mode'))
    for event in events:
        print(event.__dict__)
        regs = BTStudentRegistrations_Staging.objects.filter(RegEventId=event.id)
        rolllist = BTRollLists.objects.filter(RegEventId_id=event.id)
        for reg in regs:
            roll = rolllist.filter(student=reg.student.student).first()
            if not BTStudentRegistrations.objects.filter(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id).exists():
                s=BTStudentRegistrations(student=roll, RegEventId=reg.RegEventId, Mode=reg.Mode, sub_id=reg.sub_id)
                s.save()
        event.RegistrationStatus = 0 
        oesubs = BTSubjects.objects.filter(RegEventId=event.id,course__CourseStructure__Category__in=['OEC','OPC'])
        if len(oesubs) == 0:
            event.OERegistartionStatus=0
        event.save()
    return "done"


def cancellation_script(file, ayear):
    import pandas as pd
    file = pd.read_csv(file)
    errors=[]
    for _,row in file.iterrows():
        regno = int(row['RegNo'])
        date = row['Date']
        if int(date[:4]) == ayear:
            remark = row['remark']
            studentInfo = BTStudentInfo.objects.filter(RegNo=regno).first()
            if not studentInfo:
                errors.append(regno)
                continue
            student = studentInfo.first()
            droppedregular= BTDroppedRegularCourses.objects.filter(student_id=student.id)
            notpromoted= BTNotPromoted.objects.filter(student_id=student.id)
            notregistered =BTNotRegistered.objects.filter(Student_id=student.id)
            rolls= BTRollLists.objects.filter(student_id=student.id)
            regs =BTStudentRegistrations.objects.filter(student__student__RegNo=regno)
            grades =BTStudentGrades.objects.filter(RegId_id__in = regs.values_list('id',flat =True))
            marks = BTMarks.objects.filter(Registration__in = regs)
            BTCancelledStudentInfo(id=student.id,Remarks=remark,CancelledDate=date,RegNo=student.RegNo,RollNo=student.RollNo,Name=student.Name,Regulation=student.Regulation,Dept=student.Dept,AdmissionYear=student.AdmissionYear,Gender=student.Gender,Category=student.Category,GuardianName=student.GuardianName,Phone=student.Phone,email=student.email,Address1=student.Address1,Address2=student.Address2,Cycle=student.Cycle).save()
            for i in rolls:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledRollLists.objects.create(**i_dict)
            for i in notregistered:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledNotRegistered.objects.create(**i_dict)
            for i in regs:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledStudentRegistrations.objects.create(**i_dict)
            for i in droppedregular:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledDroppedRegularCourses.objects.create(**i_dict)
                
            for i in marks:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledMarks.objects.create(**i_dict)
            for i in grades:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledStudentGrades.objects.create(**i_dict)
            for i in notpromoted:
                i_dict = i.__dict__
                i_dict.pop('_state')
                BTCancelledNotPromoted.objects.create(**i_dict)
            BTRollLists_Staging.objects.filter(student_id=student.id).delete()
            BTMarks_Staging.objects.filter(Registration__in = regs).delete()
            BTStudentGrades_Staging.objects.filter(RegId_id__in = regs.values_list('id',flat =True)).delete()
            BTStudentRegistrations_Staging.objects.filter(student__student__RegNo=regno).delete()
            rolls.delete()
            marks.delete()
            grades.delete()
            regs.delete()
            notregistered.delete()
            notpromoted.delete()
            droppedregular.delete()
            studentInfo.delete()
    print(errors)
    print("These regno are invalid!!")
    return "Completed!!!"

def verify_grades(file, kwargs):
    file = pd.read_excel(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "no kwargs"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    headers = ['AYear', 'ASem', 'BYear', 'BSem', 'Dept', 'Regulation', 'Mode', 'SubCode', 'RMode', 'RegNo', 'Grade']
    main_headers = ['AYear', 'ASem', 'SubCode', 'RegNo', 'Regulation', 'OfferedYear', 'Dept', 'Grade', 'AttGrade']
    main_df = pd.DataFrame([], columns=main_headers)
    gen_grades_df = pd.DataFrame([], columns=headers)
    for event in regEvents:
        print(event.__dict__)
        # curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
        #     & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
        #     (file['Mode']==event.Mode)]
        if event.Mode == 'R':
            curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['Dept']==event.Dept) & \
                (file['Regulation']==event.Regulation) & (file['OfferedYear']==event.AYear)]
        else:
            curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['Dept']==event.Dept) & \
                (file['Regulation']==event.Regulation) & (file['OfferedYear']!=event.AYear)]
        main_df = pd.concat([main_df[main_headers], curr_df[main_headers]])
        curr_gen_grades_df = pd.DataFrame(BTStudentGrades_Staging.objects.filter(RegEventId=event.id).values_list('RegId__RegEventId__AYear', \
            'RegId__RegEventId__ASem', 'RegId__RegEventId__BYear', 'RegId__RegEventId__BSem', 'RegId__RegEventId__Dept',\
            'RegId__RegEventId__Regulation', 'RegId__RegEventId__Mode', 'RegId__sub_id__course__SubCode', 'RegId__Mode', 'RegId__student__student__RegNo',\
            'Grade'), columns=headers)
        gen_grades_df = pd.concat([gen_grades_df[headers], curr_gen_grades_df[headers]])
    res =pd.merge(main_df, gen_grades_df, on=['RegNo','SubCode','AYear','ASem','Dept', 'Grade'],how='outer',indicator=True)
    res.to_excel(dprefix + 'SampleRes_grades.xlsx',index=False)
    return "Done"
    
    
def not_promoted_cleansing_script():
    not_prom = BTNotPromoted.objects.filter(student__RegNo=971120)
    print(not_prom)
    error_no_event = []
    # not_prom = BTNotPromoted.objects.filter(student__RegNo=971224)
    for np in not_prom:
        with transaction.atomic():
            student_obj = np.student
            if np.PoA_sem1 == 'R':
                print(student_obj.__dict__, np.__dict__)
                regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=np.BYear, RegEventId__BSem=1, RegEventId__AYear__lte=np.AYear).first()
                if not regular_event:
                    error_no_event.append((np.student.RegNo, np.AYear, np.BYear, 1))
                else:
                    regular_event = regular_event.RegEventId
                    regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                    print([(sub.course.SubCode, sub.RegEventId.AYear)for sub in regular_subjects])
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
                regular_event = BTRollLists.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__Mode='R', RegEventId__BYear=np.BYear, RegEventId__BSem=2, RegEventId__AYear__lte=np.AYear).first()
                if not regular_event:
                    error_no_event.append((np.student.RegNo, np.AYear, np.BYear, 1))
                else:
                    regular_event = regular_event.RegEventId
                    regular_subjects = BTSubjects.objects.filter(RegEventId__id=regular_event.id)
                    print([(sub.course.SubCode, sub.RegEventId.AYear)for sub in regular_subjects])
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
    print(error_no_event)
    print("These dont have regular roll list")
    return "Completed!!!"

def dec_regs_file_upload_script(file, kwargs):
    file = pd.read_csv(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "No events"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    for event in regEvents:
        print(event.__dict__)
        curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
            & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
            (file['Mode']==event.Mode) & (file['Category']=='DEC')]
        subjects = BTSubjects.objects.filter(RegEventId_id=event.id, course__CourseStructure__Category='DEC')
        rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
        for rIndex, row in curr_df.iterrows():
            regNo = row['RegNo']
            mode = 1
            if event.Mode == 'B':
                mode = row['RMode']
            subject = subjects.filter(course__SubCode=row['SubCode']).first()
            if not BTStudentRegistrations_Staging.objects.filter(student=rolls.filter(student__RegNo=regNo).first(), RegEventId_id=event.id,Mode=mode,\
                sub_id_id=subject.id).exists():
                reg = BTStudentRegistrations_Staging(student=rolls.filter(student__RegNo=regNo).first(), RegEventId_id=event.id,Mode=mode,\
                    sub_id_id=subject.id)
                reg.save()
    return "Completed!!"

def oe_roll_lists_script(file, kwargs):
    file = pd.read_csv(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "No events"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    for event in regEvents:
        print(event.__dict__)
        curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
            & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
            (file['Mode']==event.Mode) & (file['Category']=='OPC')]
        subjects = BTSubjects.objects.filter(RegEventId_id=event.id, course__CourseStructure__Category='OPC')
        rolls = BTRollLists_Staging.objects.filter(RegEventId_id=event.id)
        BTOpenElectiveRollLists.objects.filter(RegEventId_id=event.id).delete()
        for rIndex, row in curr_df.iterrows():
            subject = subjects.filter(course__SubCode=row['SubCode']).first()
            if not BTOpenElectiveRollLists.objects.filter(student_id=rolls.filter(student__RegNo=row['RegNo']).first().id, RegEventId_id=event.id, subject_id=subject.id, Section='NA').exists():
                new_row = BTOpenElectiveRollLists(student_id=rolls.filter(student__RegNo=row['RegNo']).first().id, RegEventId_id=event.id, subject_id=subject.id, Section='NA')
                new_row.save()
    return "Completed!!"

def oe_registrations(file, kwargs):
    file = pd.read_csv(file)
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "No events"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    for event in regEvents:
        print(event.__dict__)
        curr_df = file[(file['AYear']==event.AYear) & (file['ASem']==event.ASem) & (file['BYear']==event.BYear)\
            & (file['BSem']==event.BSem) & (file['Dept']==event.Dept) & (file['Regulation']==event.Regulation) & \
            (file['Mode']==event.Mode) & (file['Category']=='OPC')]
        roll_list = BTOpenElectiveRollLists.objects.filter(RegEventId_id=event.id)
        for rIndex, row in curr_df.iterrows():
            roll = roll_list.filter(student__student__RegNo=row['RegNo']).first()
            mode = 1
            if event.Mode != 'R':
                mode = row['RMode']
            if not BTStudentRegistrations_Staging.objects.filter(student_id=roll.student.id, RegEventId_id=roll.RegEventId_id, sub_id_id=roll.subject.id).exists():
                new_reg = BTStudentRegistrations_Staging(student_id=roll.student.id, RegEventId_id=roll.RegEventId_id, sub_id_id=roll.subject.id, Mode=mode)
                new_reg.save()
            else:
                BTStudentRegistrations_Staging.objects.filter(student_id=roll.student.id, RegEventId_id=roll.RegEventId_id, sub_id_id=roll.subject.id).update(Mode=mode)
    return "Completed!!!"


def check_registrations_finalize_script(kwargs):
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
    else:
        return "No events"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
        BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    execess_credits_students = []
    insuff_credits_students = []
    for event in regEvents:
        print(event.__dict__)
        rolllist = BTRollLists.objects.filter(RegEventId_id=event.id)
        regs = BTStudentRegistrations_Staging.objects.filter(student__student__id__in=rolllist.values_list('student_id',flat=True), \
                RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__BYear=event.BYear, RegEventId__Dept=event.Dept)
        curriculum = BTCourseStructure.objects.filter(BYear=event.BYear, BSem=event.BSem, Dept=event.Dept, Regulation=event.Regulation)

        for roll in rolllist:
            study_credits = regs.filter(student__student=roll.student, Mode=1).aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
            exam_credits = regs.filter(student__student=roll.student, Mode=0).aggregate(Sum('sub_id__course__CourseStructure__Credits')).get('sub_id__course__CourseStructure__Credits__sum') or 0
        
            if study_credits > 32 or (study_credits+exam_credits) > 34:
                execess_credits_students.append((event.__str__(), roll.student.RegNo))
            
            if event.Mode == 'R':
                dropped_courses = BTDroppedRegularCourses.objects.filter(student=roll.student, RegEventId__AYear=event.AYear, RegEventId__ASem=event.ASem, RegEventId__BYear=event.BYear, RegEventId__Dept=event.Dept, RegEventId__Regulation=event.Regulation, RegEventId__Mode='R')
                student_regs = regs.filter(student__student=roll.student)
                for cs in curriculum:
                    cs_count = student_regs.filter(sub_id__course__CourseStructure_id=cs.id).count()
                    dropped_cs_count = dropped_courses.filter(subject__course__CourseStructure_id=cs.id).count()
                    if (dropped_cs_count+cs_count) != cs.count:
                        insuff_credits_students.append((event.__str__(), roll.student.RegNo))
                        break
    for _ in execess_credits_students:
        print(_)
    print("These students have excess credits in the registrations")
    for _ in insuff_credits_students:
        print(_)
    print("These students have unequal courses corresponding to their slots.")
    return "Completed!!"        

def finalize_marks(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
        return "No Events!!!!"
    for event in regEvents:
        print(event.__dict__)
        marks_objs = BTMarks_Staging.objects.filter(Registration__RegEventId_id=event.id)
        for mark in marks_objs:
            BTMarks.objects.filter(Registration=mark.Registration).update(Marks=mark.Marks, TotalMarks=mark.TotalMarks)
        event.MarkStatus = 0
        event.save()
    return "Completed!!"

def finalize_grades(kwargs):
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    regEvents = BTRegistrationStatus.objects.filter(AYear__in=kwargs.get('AYear'), ASem__in=kwargs.get('ASem'), BYear__in=kwargs.get('BYear'),
            BSem__in=kwargs.get('BSem'), Dept__in=kwargs.get('Dept'), Regulation__in=kwargs.get('Regulation'), Mode__in=kwargs.get('Mode'))
    if not regEvents:
        return "No Events!!!!"
    for event in regEvents:
        print(event.__dict__)
        grades_objs = BTStudentGrades_Staging.objects.filter(RegId_RegEventId_id=event.id)
        for grade in grades_objs:
            fgrade = BTStudentGrades(RegId_id=grade.RegId.id, RegEventId=grade.RegEventId, Regulation=grade.Regulation, Grade=grade.Grade, AttGrade=grade.AttGrade)
            fgrade.save()
        event.GradeStatus = 0
        event.save()
    RefreshMaterializedViews()
    return "Completed!!"

def RefreshMaterializedViews():
    cursor = connection.cursor()

    try:
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentGradePointsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentGradePoints_StagingMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentBacklogsMV\" WITH DATA;")
        cursor.execute("REFRESH MATERIALIZED VIEW public.\"BTStudentMakeupBacklogsMV\" WITH DATA;")
    finally:
        cursor.close()

dataPrefix = '/home/examsection/Desktop/Data/MarksDB/'
duprefix = '/home/examsection/Desktop/Data/'
aprefix = '/home/examsection/Desktop/awsp_testing_v2/database_recreate/'
section_prefix = '/home/examsection/Desktop/Data/SectionWise/2019/'
dprefix = '/home/examsection/Downloads/'
kwargs = {'AYear':2019, 'ASem':2, 'BYear':1, 'BSem':2, 'Dept':10, 'Regulation':3.1, 'Mode':'R'}
# kwargs_grades = {'AYear':[2019], 'ASem':[1,2], 'BYear':[1], 'BSem':[1,2], 'Dept':[9,10], 'Regulation':[2], 'Mode':['B']}
# kwargs_grades = {'AYear':[2019], 'ASem':[1,2], 'BYear':[3], 'BSem':[1,2], 'Dept':[i for i in range(1,9)], 'Regulation':[2], 'Mode':['R']}
# kwargs_grades = {'AYear':[2019], 'ASem':[1,2], 'BYear':[3], 'BSem':[1,2], 'Dept':[i for i in range(1,9)], 'Regulation':[1], 'Mode':['B']}
# kwargs_grades = {'AYear':[2019], 'ASem':[3], 'BYear':[3], 'BSem':[2], 'Dept':[6,5], 'Regulation':[1], 'Mode':['M']}
# kwargs_grades = {'AYear':[2019], 'ASem':[1], 'BYear':[4], 'BSem':[1], 'Dept':[1], 'Regulation':[1], 'Mode':['R']}
# kwargs_grades = {'AYear':[2019], 'ASem':[3], 'BYear':[4], 'BSem':[1], 'Dept':[4,5,6], 'Regulation':[1], 'Mode':['M']}
kwargs_grades = {'AYear':[2019], 'ASem':[1,2], 'BYear':[4], 'BSem':[1,2], 'Dept':[i for i in range(1,9)], 'Regulation':[1], 'Mode':['R']}
# print(roll_list_script(kwargs_grades))
# print(rolls_finalize_script(kwargs_grades))
# print(regular_regs_script(kwargs_grades))
# print(backlog_registrations(dataPrefix+'2019-Marks-Data-4.xlsx', kwargs_grades))
# print(dec_regs_file_upload_script(dataPrefix+'electives_rolls.csv', kwargs_grades))
# print(oe_roll_lists_script(dataPrefix+'electives_rolls.csv', kwargs_grades))
# print(oe_registrations(dataPrefix+'electives_rolls.csv', kwargs_grades))
# print(check_registrations_finalize_script(kwargs_grades))
# print(registrations_finalize(kwargs_grades))
# print(faculty_assignment(**kwargs_grades))
# print(add_marks(dataPrefix+'2019-Marks-Data-4.xlsx', kwargs_grades))
# print(add_grades_threshold(dataPrefix+'Thresholds-R15-R18-R20.xlsx', kwargs_grades))
# print(add_grades_threshold(dataPrefix+'Thresholds-R17.xlsx', kwargs_grades))
# print(add_Rixgrades(dataPrefix+'2019-Grades-RIX.xlsx', kwargs_grades))
# print(add_Rixgrades(aprefix+'2019-I-BT-RGrades-Sem-I-R.xlsx', kwargs))
# print(generate_grades(**kwargs_grades))
# print(verify_grades(aprefix+'All-Grades-2021-v7.xlsx', kwargs_grades))
# print(finalize_marks(kwargs_grades))
# print(finalize_grades(kwargs_grades))
