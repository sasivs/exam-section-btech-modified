import os
import pandas as pd
from ADAUGDB.models import BTRegistrationStatus, BTCourseStructure, BTCourses
from BTco_ordinator.models import BTStudentRegistrations, BTNotPromoted, BTNPRStudentRegistrations, BTNPRRollLists, BTNPRMarks\
    , BTSubjects
from BTExamStaffDB.models import BTStudentInfo
from BTfaculty.models import BTAttendance_Shortage, BTMarks, BTMarks_Staging

def make_dir(home):
    if not os.path.exists(home):
        os.makedirs(home)

def build_db():
    student_regs = BTStudentRegistrations.objects.all()
    events = BTRegistrationStatus.objects.all()
    roll_list = []
    student_regs_list = []
    student_info = BTStudentInfo.objects.all()
    for reg in student_regs:
        student = student_info.filter(RegNo=reg.RegNo)
        event = events.filter(id=reg.RegEventId_id)
        newRow = [student.id, event.id]
        if event.BYear == 1:
            newRow.append(event.Dept)
        else:
            newRow.append(0)
        newRow.append('NA')
        if not newRow in roll_list:
            roll_list.append(newRow)
            id = len(roll_list)
        else:
            id = roll_list.index(newRow)+1
        student_regs_list.append([reg.id, id, event.id, reg.Mode, reg.sub_id_id])
    regs_frame = pd.DataFrame(student_regs_list, columns=['id', 'student_id', 'RegEventId_id', 'Mode', 'sub_id_id'])
    rolls_frame = pd.DataFrame(roll_list, columns=['student_id', 'RegEventId_id', 'Cycle', 'Section'])
    rolls_frame.index = rolls_frame.index + 1
    rolls_frame.index.name = 'id'
    
    not_promoted_records = BTNotPromoted.objects.all().values_list()
    not_promoted_frame = pd.DataFrame(list(not_promoted_records), columns=['id', 'AYear', 'BYear', 'Regulation', 'student_id', 'PoA_sem1'])
    not_promoted_frame['PoA_sem2'] = not_promoted_frame['PoA_sem1']

    regs_frame.to_excel(r"C:\Users\sasib\Desktop\db\btech\registrations.xlsx", index=False)
    rolls_frame.to_excel(r"C:\Users\sasib\Desktop\db\btech\rollLists.xlsx")
    not_promoted_frame.to_excel(r"C:\Users\sasib\Desktop\db\btech\rollLists.xlsx",index=False)


def prepare_excel():
    import pandas as pd
    registrations_new = BTStudentRegistrations.objects.filter(RegEventId__AYear__lt=2019).\
        values_list('id', 'student__student__RegNo', 'RegEventId_id', 'Mode', 'sub_id_id')
    print(registrations_new)
    print(len(registrations_new))
    df = pd.DataFrame.from_records(registrations_new)
    print(df)
    df.to_csv('registrations_till_2019_v1.csv', index=False)

def prepare_marks(file):
    import pandas as pd
    file = pd.read_csv(file)
    error_multiple = []
    error_no_reg = []
    for _, row in file.iterrows():
        reg = BTStudentRegistrations.objects.filter(RegEventId__AYear=row['AYear'], RegEventId__BYear=row['BYear'],\
            RegEventId__BSem=row['BSem'], RegEventId__ASem=row['ASem'], RegEventId__Mode=row['Mode'],\
            RegEventId__Dept=row['Dept'], RegEventId__Regulation=row['Regulation'], student__student__RegNo=row['RegNo'],\
            sub_id__course__SubCode=row['SubCode'])
        if len(reg)>1:
            error_multiple.append(row)
        elif not reg:
            error_no_reg.append(row)
        else:
            reg = reg.first()
            if not BTMarks.objects.filter(Registration_id=reg.id).exists():
                mark = BTMarks(Registration_id=reg.id, Marks=row['Marks'], TotalMarks=row['TotalMarks'])
                mark.save()
            else:
                BTMarks.objects.filter(Registration_id=reg.id).update(Marks=row['Marks'], TotalMarks=row['TotalMarks'])
            if not BTMarks_Staging.objects.filter(Registration_id=reg.id).exists():
                mark = BTMarks_Staging(Registration_id=reg.id, Marks=row['Marks'], TotalMarks=row['TotalMarks'])
                mark.save()
            else:
                BTMarks_Staging.objects.filter(Registration_id=reg.id).update(Marks=row['Marks'], TotalMarks=row['TotalMarks'])
    print(error_multiple)
    print('These rows have multiple registration rows')
    print(error_no_reg)
    print("These rows have no reg rows")
    return "Done"

def prepare_marks_npr(file):
    import pandas as pd
    file = pd.read_csv(file)
    error_multiple = []
    error_no_reg = []
    for _, row in file.iterrows():
        event = BTRegistrationStatus.objects.filter(AYear=row['AYear'], BYear=row['BYear'],BSem=row['BSem'], \
            ASem=row['ASem'], Mode=row['Mode'],Dept=row['Dept'], Regulation=row['Regulation']).first()
        student = BTStudentInfo.objects.filter(RegNo=row['RegNo']).first()
        roll = BTNPRRollLists.objects.filter(RegEventId_id=event.id, student_id=student.id).first()
        reg = BTNPRStudentRegistrations.objects.filter(RegEventId_id=event.id, student_id=roll.id)
        subjects = BTSubjects.objects.filter(id__in=reg.values_list('sub_id_id', flat=True))
        subject = subjects.filter(course__SubCode=row['SubCode']).first()
        req_reg = reg.filter(sub_id_id=subject.id)
        if len(req_reg)>1:
            error_multiple.append(row)
        elif not req_reg:
            error_no_reg.append(row)
        else:
            reg = req_reg.first()
            if not BTNPRMarks.objects.filter(Registration_id=reg.id).exists():
                mark = BTNPRMarks(Registration_id=reg.id, Marks=row['Marks'], TotalMarks=row['TotalMarks'])
                mark.save()
            else:
                BTNPRMarks.objects.filter(Registration_id=reg.id).update(Marks=row['Marks'], TotalMarks=row['TotalMarks'])
            # if not BTMarks_Staging.objects.filter(Registration_id=reg.id).exists():
            #     mark = BTMarks_Staging(Registration_id=reg.id, Marks=row['Marks'], TotalMarks=row['TotalMarks'])
            #     mark.save()
            # else:
            #     BTMarks_Staging.objects.filter(Registration_id=reg.id).update(Marks=row['Marks'], TotalMarks=row['TotalMarks'])
    print(error_multiple)
    print('These rows have multiple registration rows')
    print(error_no_reg)
    print("These rows have no reg rows")
    return "Done"


def update_rigid_column():
    BTCourseStructure.objects.filter(BYear__gte=2, Category='MDC').update(Rigid=False)

def update_course_credits():
    courses = BTCourses.objects.all()
    for course in courses:
        course.Credits = course.CourseStructure.Credits
        course.save()

update_course_credits()