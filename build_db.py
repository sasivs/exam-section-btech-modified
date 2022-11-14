import os
import pandas as pd
from ADAUGDB.models import BTRegistrationStatus
from BTco_ordinator.models import BTStudentRegistrations, BTNotPromoted
from BTExamStaffDB.models import BTStudentInfo

def make_dir(home):
    if not os.path.exists(home):
        os.makedirs(home)

def build_db(years):
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

