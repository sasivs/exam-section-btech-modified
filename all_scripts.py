
from ADAUGDB.models import BTGradePoints, BTRegistrationStatus
from BTco_ordinator.models import BTSubjects, BTFacultyAssignment, BTStudentRegistrations
from BTfaculty.models import BTAttendance_Shortage, BTGradesThreshold, BTMarks, BTMarks_Staging, BTStudentGrades_Staging
from BTExamStaffDB.models import BTFacultyInfo, BTIXGradeStudents
import pandas as pd


def faculty_assignment(**kwargs):
    '''
    Dept can be given in the form of list consisting of departments.
    All the remaining arguments are not lists
    '''
    print(kwargs)
    if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
        return "Provide the required arguments!!!!"
    if kwargs.get('Mode') == 'R':
        regEvents = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), ASem=kwargs.get('ASem'), BYear=kwargs.get('BYear'), BSem=kwargs.get('BSem'), \
            Regulation=kwargs.get('Regulation'), Mode=kwargs.get('Mode'))
        if not regEvents:
            return "No Events!!!!"
        depts = kwargs.get('Dept')
        if not kwargs.get('Dept') and kwargs.get('BYear')!=1:
            depts = [1,2,3,4,5,6,7,8]
        elif not kwargs.get('Dept') and kwargs.get('BYear')==1:
            depts = [9,10]
        for dept in depts:
            print(regEvents.filter(Dept=dept).first().__dict__)
            regEventId = regEvents.filter(Dept=dept).first().id
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
    elif kwargs.get('Mode') == 'M' or kwargs.get('Mode') == 'B':
        regEvents = BTRegistrationStatus.objects.filter(AYear=kwargs.get('AYear'), ASem=kwargs.get('ASem'), BYear=kwargs.get('BYear'), BSem=kwargs.get('BSem'), \
            Regulation=kwargs.get('Regulation'), Mode=kwargs.get('Mode'))
        if not regEvents:
            return "No Events!!!!"
        depts = kwargs.get('Dept')
        if not kwargs.get('Dept') and kwargs.get('BYear')!=1:
            depts = [1,2,3,4,5,6,7,8]
        elif not kwargs.get('Dept') and kwargs.get('BYear')==1:
            depts = [9,10]
        for dept in depts:
            print(regEvents.filter(Dept=dept).first().__dict__)
            regEventId = regEvents.filter(Dept=dept).first().id
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


def add_marks(file):
    import pandas as pd
    file = pd.read_excel(file)
    invalid_rows=[]
    for rIndex, row in file.iterrows():
        print(row)
        regEvent = BTRegistrationStatus.objects.filter(AYear=row['AYear'], ASem=row['ASem'], BYear=row['BYear'], BSem=row['BSem'], Dept=row['Dept'], Regulation=row['Regulation'], Mode=row['Mode']).first()
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
                    invalid_rows.append((rIndex,row))
                else:
                    marks[outer][inner] = str(row[mark_index])
                mark_index+=1
        marks = ['+'.join(mark) for mark in marks]
        marks_string = ','.join(marks)
        marks_row.Marks = marks_string
        marks_row.TotalMarks = marks_row.get_total_marks()
        marks_row.save()
    if invalid_rows:
        print("These rows have marks greater than intended maximum marks")
        print(invalid_rows)
    return "Completed!!!!"


def add_grades_threshold(file, kwargs=None):
    file = pd.read_excel(file)
    error_rows=[]
    if kwargs:
        if not (kwargs.get('Mode') or kwargs.get('AYear') or kwargs.get('BYear') or kwargs.get('BSem') or kwargs.get('ASem') or kwargs.get('Regulation')):
            return "Provide the required arguments!!!!"
        file = file[(file['AYear']==kwargs.get('AYear')) & (file['ASem']==kwargs.get('ASem')) & (file['BYear']==kwargs.get('BYear'))\
            & (file['BSem']==kwargs.get('BSem')) & (file['Dept']==kwargs.get('Dept')) & (file['Regulation']==kwargs.get('Regulation')) & \
            file['Mode']==kwargs.get('Mode')]
    for rIndex, row in file.iterrows():
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
                    error_rows.append(row)
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
        print('Error'+ er['SubCode'])

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
                error_events.append((event, subject.course.SubCode))
            if mark.Registration.Mode == 1:
                promote_thresholds = subject.course.MarkDistribution.PromoteThreshold
                promote_thresholds = promote_thresholds.split(',')
                promote_thresholds = [thr.split('+') for thr in promote_thresholds]
                marks_list = mark.Marks.split(',')
                marks_list = [m.split('+') for m in marks_list]
                graded = False
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