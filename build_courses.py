from ADAUGDB.models import BTMarksDistribution, BTCourseStructure, BTCourses, BTRegistrationStatus
from BTco_ordinator.models import BTSubjects
from BTco_ordinator.models import BTNotRegistered, BTStudentGradePoints, BTNotPromoted, BTRollLists, BTStudentBacklogs, BTDroppedRegularCourses, BTStudentRegistrations,\
    BTNPRDroppedRegularCourses, BTNPRMarks, BTNPRNotRegistered, BTNPRRollLists, BTNPRStudentGrades, BTNPRStudentRegistrations, BTRollLists_Staging, BTStudentRegistrations_Staging,\
        BTSubjects
from BTfaculty.models import BTStudentGrades, BTMarks, BTMarks_Staging, BTStudentGrades_Staging
import copy
from django.db import transaction

'''
DB Query: 
select bts."SubCode", bts."SubName", bts."Creditable", 
bts."Credits", bts."Type", bts."Category", bts."OfferedBy",
bts."DistributionRatio", bts."Distribution", bts."DistributionNames"
, bts."PromoteThreshold", btrs."BYear", btrs."BSem", btrs."Dept", btrs."Regulation"
from ("BTSubjects" btss join "BTMarkDistribution" btm on btss."MarkDistribution_id"=btm."id")bts
join "BTRegistration_Status" btrs on bts."RegEventId_id"=btrs."id"
'''

def build_course_structure(file):
    import pandas as pd
    file = pd.read_csv(file)
    file = file.drop_duplicates(subset=['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', 'Type', 'Category', 'DistributionRatio', 'Distribution', 'DistributionNames', 'PromoteThreshold'])
    # file['lectures'] = 0
    # file['tutorials'] = 0
    # file['practicals'] = 0
    # course_structure_data = file.drop_duplicates(subset=['BYear', 'BSem', 'Dept', 'Regulation', 'Category', 'Type', 'Creditable', 'Credits'])
    # course_structure_data = course_structure_data[['BYear', 'BSem', 'Dept', 'Regulation', 'Category', 'Type', 'Creditable', 'Credits']]
    course_structure_data = file[['BYear', 'BSem', 'Dept', 'Regulation', 'Category', 'Type', 'Creditable', 'Credits']]
    # print(course_structure_data)
    pd.options.display.multi_sparse = False
    cs_file = course_structure_data.value_counts().reset_index(name='count')
    # cs_file.index.name = 'id'
    # cs_file.index += 1
    pd.options.display.multi_sparse = True
    # print(cs_file)
    cs_file.to_excel(r"C:\Users\sasib\Desktop\db\btech\course_structure_from_2019_1.xlsx", index=False)

def build_courses_file(file):
    import pandas as pd
    file = pd.read_csv(file)
    file = file.drop_duplicates(subset=['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', 'Type', 'Category', 'DistributionRatio', 'Distribution', 'DistributionNames', 'PromoteThreshold'])
    file['lectures'] = 0
    file['tutorials'] = 0
    file['practicals'] = 0
    file['MarkDistribution'] = ''
    for _, row in file.iterrows():
        if row["Type"] == 'THEORY':
            file.at[_,'lectures'] = row['Credits']
        elif row["Type"] == 'LAB':
            file.at[_,'practicals'] = row['Credits']-1
            file.at[_,'tutorials'] = 1
        else:
            file.at[_,'lectures'] = row['Credits']
        distribution_marks = row['Distribution'].split(',')
        marks = [row.split('+') for row in distribution_marks]
        ncolumns = 0
        for dis in marks: ncolumns+=len(dis)
        t_marks = [['100' for _ in range(len(row))] for row in marks]
        t_marks = ['+'.join(mark) for mark in t_marks]
        t_marks = ','.join(t_marks)
        if ncolumns == 4: dis_names = 'Minor-I'+'+'+'MID'+'+'+'Minor-II'+'+'+'END'
        elif ncolumns == 2: dis_names = 'Internal'+'+'+'External'
        elif ncolumns == 6: dis_names = 'Minor-I'+'+'+'MID'+'+'+'Minor-II'+'+'+'END'+','+'Internal'+'+'+'External'
        elif ncolumns == 1: dis_names = 'End'
        elif ncolumns == 3: dis_names = 'Con+Mid+End'
        else: print(ncolumns); print(row); break
        # print(t_marks)
        # print(row['PromoteThreshold'])
        # print(dis_names)
        distribution_string = t_marks+';'+str(row['PromoteThreshold'])+';'+dis_names
        # print(distribution_string)
        file.at[_,'MarkDistribution'] = distribution_string
        # break

    course_data = file[['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', 'Type', 'Category', 'lectures', 'tutorials', 'practicals', 'DistributionRatio', 'MarkDistribution']]
    course_data = course_data.drop_duplicates(subset=['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', 'Type', 'Category', 'lectures', 'tutorials', 'practicals', 'DistributionRatio', 'MarkDistribution'], ignore_index=True)
    course_data.to_excel(r"C:\Users\sasib\Desktop\db\btech\courses_from_2019.xlsx", index=False)

def get_marks_distribution_file(file):
    import pandas as pd
    file = pd.read_csv(file)
    file = file.drop_duplicates(subset=['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', 'Type', 'Category', 'DistributionRatio', 'Distribution', 'DistributionNames', 'PromoteThreshold'])
    for _, row in file.iterrows():
        distribution_marks = row['Distribution'].split(',')
        marks = [row.split('+') for row in distribution_marks]
        ncolumns = 0
        for dis in marks: ncolumns+=len(dis)
        t_marks = [['100' for _ in range(len(row))] for row in marks]
        t_marks = ['+'.join(mark) for mark in t_marks]
        t_marks = ','.join(t_marks)
        if ncolumns == 4: dis_names = 'Minor-I'+'+'+'MID'+'+'+'Minor-II'+'+'+'END'
        elif ncolumns == 2: dis_names = 'Internal'+'+'+'External'
        elif ncolumns == 6: dis_names = 'Minor-I'+'+'+'MID'+'+'+'Minor-II'+'+'+'END'+','+'Internal'+'+'+'External'
        elif ncolumns == 1: dis_names = 'END'
        elif ncolumns == 3: dis_names = 'Con+MID+END'
        else: print(ncolumns); print(row); break
        if not BTMarksDistribution.objects.filter(Regulation=row['Regulation'], Distribution=t_marks, DistributionNames=dis_names, PromoteThreshold=row['PromoteThreshold']).exists():
            new_row = BTMarksDistribution(Regulation=row['Regulation'], Distribution=t_marks, DistributionNames=dis_names, PromoteThreshold=row['PromoteThreshold'])
            new_row.save()

def get_course_structure_file(file):
    import pandas as pd
    file = pd.read_csv(file)
    org_file = copy.deepcopy(file)
    file = file.drop_duplicates(subset=['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', 'Type', 'Category', 'DistributionRatio', 'MarkDistribution_id'])
    file['lectures'] = 0
    file['tutorials'] = 0
    file['practicals'] = 0
    mark_dis_rows = []
    for _, row in file.iterrows():
        if row["Type"] == 'THEORY':
            row['lectures'] = row['Credits']
        else:
            row['practicals'] = row['Credits']-1
            row['tutorials'] = 1
        mark_dis = BTMarksDistribution.objects.get(id=int(row['MarkDistribution_id']))
        distribution_marks = mark_dis.Distribution.split(',')
        marks = [row.split('+') for row in distribution_marks]
        t_marks = [['100' for _ in range(len(row))] for row in marks]
        t_marks = ['+'.join(mark) for mark in t_marks]
        t_marks = ','.join(t_marks)
        ncolumns = len(mark_dis.distributions())
        if ncolumns == 4: dis_names = 'Minor-I'+'+'+'MID'+'+'+'Minor-II'+'+'+'END'
        elif ncolumns == 2: dis_names = 'Internal'+'+'+'External'
        mark_dis_row = (row['Regulation'], t_marks, dis_names, mark_dis.PromoteThreshold)
        if mark_dis_row not in mark_dis_rows:
            mark_dis_rows.append(mark_dis_row)
        file.at[_,'MarkDistribution_id'] = mark_dis_rows.index(mark_dis_row)+1
    print(file)
    mark_dis_dataset = pd.DataFrame(mark_dis_rows, columns=['Regulation', 'Distribution', 'DistributionNames', 'PromoteThreshold'])
    mark_dis_dataset.index = mark_dis_dataset.index+1 
    mark_dis_dataset.index.name = 'id'
    print(mark_dis_dataset)
    file = file.drop_duplicates(subset=['SubCode', 'SubName', 'BYear', 'BSem', 'Dept', 'OfferedBy', 'Regulation', 'Creditable', 'Credits', \
        'Type', 'Category', 'DistributionRatio', 'MarkDistribution_id', 'lectures', 'tutorials', 'practicals'])
    file['CourseStructure_id'] = 0
    course_structure_data = file[['BYear', 'BSem', 'Dept', 'Regulation', 'Category', 'Type', 'Creditable', 'Credits']]
    pd.options.display.multi_sparse = False
    cs_file = course_structure_data.value_counts().reset_index(name='count')
    cs_file.index.name = 'id'
    cs_file.index += 1
    pd.options.display.multi_sparse = True
    print(cs_file)
    for _, row in file.iterrows():
        file.at[_,'CourseStructure_id'] = cs_file.loc[(cs_file['BYear']==row['BYear']) & (cs_file['BSem']==row['BSem']) & (cs_file['Dept']==row['Dept']) & \
            (cs_file['Regulation']==row['Regulation']) & (cs_file['Category']==row['Category']) & (cs_file['Type']==row['Type']) & \
                (cs_file['Creditable']==row['Creditable']) & (cs_file['Credits']==row['Credits'])].index[0]
    
    course_data = file[['SubCode', 'SubName', 'OfferedBy', 'CourseStructure_id', 'lectures', 'tutorials', 'practicals', 'DistributionRatio', 'MarkDistribution_id']]
    
    course_data = course_data.drop_duplicates(subset=['SubCode', 'SubName', 'OfferedBy', 'CourseStructure_id', 'lectures', 'tutorials', 'practicals', 'DistributionRatio', 'MarkDistribution_id'], ignore_index=True)
    course_data.index = course_data.index + 1
    course_data.index.name = 'id'
    print(course_data)

    subjects_data = []
    for _, row in org_file.iterrows():
        new_row = [row['id'], row['RegEventId_id']]
        cs_id = cs_file.loc[(cs_file['BYear']==row['BYear']) & (cs_file['BSem']==row['BSem']) & (cs_file['Dept']==row['Dept']) & \
            (cs_file['Regulation']==row['Regulation']) & (cs_file['Category']==row['Category']) & (cs_file['Type']==row['Type']) & \
                (cs_file['Creditable']==row['Creditable']) & (cs_file['Credits']==row['Credits'])].index[0]
        course_id = course_data.loc[(course_data['SubCode']==row['SubCode']) & (course_data['SubName']==row['SubName']) & (course_data['OfferedBy']==row['OfferedBy'])&\
            (course_data['CourseStructure_id']==cs_id)].index[0]
        new_row.append(course_id)
        subjects_data.append(new_row)
    subjects_frame = pd.DataFrame(subjects_data, columns=['id', 'RegEventId_id', 'course_id'])
    print(subjects_frame)
        
    mark_dis_dataset.to_csv("/home/examsection/Desktop/awsp_testing_v2/database_recreate/Marks_distribution.csv")
    cs_file.to_csv("/home/examsection/Desktop/awsp_testing_v2/database_recreate/course_structure.csv")
    course_data.to_csv("/home/examsection/Desktop/awsp_testing_v2/database_recreate/courses.csv")
    subjects_frame.to_csv("/home/examsection/Desktop/awsp_testing_v2/database_recreate/Subjects_new_db_2018.csv", index=False)
# get_course_structure_file(r"C:\Users\sasib\Desktop\db\btech\phy_Subjects.xlsx")


def course_structure_check(file):
    import pandas as pd
    file = pd.read_csv(file)
    error=[]
    error_rows = []
    for _, row in file.iterrows():
        if BTCourseStructure.objects.filter(BYear=row['BYear'], BSem=row['BSem'], Dept=row['Dept'], Regulation=row['Regulation'],\
            Category=row['Category'], Type=row['Type'], Creditable=row['Creditable'], Credits=row['Credits']).exists():
            BTCourseStructure.objects.filter(BYear=row['BYear'], BSem=row['BSem'], Dept=row['Dept'], Regulation=row['Regulation'],\
            Category=row['Category'], Type=row['Type'], Creditable=row['Creditable'], Credits=row['Credits']).update(count=row['count'])
        else:
            error.append(row)
    course_structure_rows = BTCourseStructure.objects.filter(Regulation=1.0, Dept=row['Dept'])
    for row in course_structure_rows:
        sub_frame = file.loc[(file['BYear']==row.BYear) & (file['BSem']==row.BSem) & (file['Dept']==row.Dept) & \
            (file['Regulation']==row.Regulation) & (file['Category']==row.Category) & (file['Type']==row.Type)& \
                (file['Creditable']==row.Creditable)&(file['Credits']==row.Credits)&(file['count']==row.count)]
        if sub_frame.shape[0] != 1:
            error_rows.append(row.__dict__)
    print(error)
    print("These rows are there in file but not in table")
    print(error_rows)
    print("These rows are there in table but not in file")
    return "Completed!!"

def update_courses(file):
    import pandas as pd
    file = pd.read_csv(file)
    subjects = BTSubjects.objects.filter(RegEventId__AYear__lt=2019).order_by('id')
    errors = []
    for sub in subjects:
        #esf = event_subjects_frame
        esf = file[(file['AYear']==sub.RegEventId.AYear) & (file['ASem']==sub.RegEventId.ASem) & (file['BYear']==sub.RegEventId.BYear)\
            & (file['BSem']==sub.RegEventId.BSem) & (file['Dept']==sub.RegEventId.Dept) & (file['Regulation']==sub.RegEventId.Regulation) & \
            (file['Mode']==sub.RegEventId.Mode)]
        
        #rs=required_subject
        rs = esf.loc[(esf['SubCode']==sub.course.SubCode)].iloc[0]
        
        required_course_structure = BTCourseStructure.objects.filter(BYear=rs['BYear'], BSem=rs['BSem'], Dept=rs['Dept'], \
            Regulation=rs['Regulation'], Category=rs['Category'].upper(), Type=rs['Type'].upper(), Creditable=rs['Creditable'], \
                Credits=rs['Credits']).first()
        
        if not required_course_structure:
            errors.append(rs)
            continue
        
        if BTCourses.objects.filter(SubCode=sub.course.SubCode, SubName=sub.course.SubName, \
            CourseStructure_id=required_course_structure.id, DistributionRatio=sub.course.DistributionRatio, \
                MarkDistribution_id=sub.course.MarkDistribution_id).exists():
            required_course = BTCourses.objects.filter(SubCode=sub.course.SubCode, SubName=sub.course.SubName, \
            CourseStructure_id=required_course_structure.id, DistributionRatio=sub.course.DistributionRatio, \
                MarkDistribution_id=sub.course.MarkDistribution_id).first()
            sub.course_id = required_course.id
            sub.save()
        
        else:
            BTCourses.objects.filter(id=sub.course.id).update(CourseStructure_id=required_course_structure.id)


    print(errors)
    print("These rows do not have course structure")
    return "Completed!!!"        


def not_promoted_repopulate_script():
    not_prom = BTNotPromoted.objects.all()
    for np in not_prom:
        with transaction.atomic():
            student_obj = np.student
            if np.PoA_sem1 == 'R' and np.PoA_sem2 == 'R':
                rolls = BTNPRRollLists.objects.filter(student_id=student_obj.id)
                events = BTRegistrationStatus.objects.filter(Mode='R', BYear=np.BYear, BSem=1)
                regular_rolls = BTRollLists.objects.filter(RegEventId_id__in=events.values_list('id', flat=True), student__RegNo=student_obj.RegNo)
                regular_regs = BTNPRStudentRegistrations.objects.filter(RegEventId_id__in=events.values_list('id', flat=True), student_id__in=regular_rolls.values_list('id', flat=True))
                subjects = BTSubjects.objects.filter(id__in=regular_regs.values_list('sub_id_id', flat=True))
                total_regs_1 = BTNPRStudentRegistrations.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student_id__in=regular_rolls.values_list('id', flat=True))
                total_regs = BTNPRStudentRegistrations.objects.filter(student_id__in=rolls.values_list('id', flat=True))
                total_regs = total_regs | total_regs_1
                grades = BTNPRStudentGrades.objects.filter(RegId__in=total_regs.values_list('id', flat=True))
                marks = BTNPRMarks.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True))
                not_registered = BTNPRNotRegistered.objects.filter(Student_id=student_obj.id)
                dropped_regular = BTNPRDroppedRegularCourses.objects.filter(student_id=student_obj.id)
                for i in rolls:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTRollLists.objects.create(**i_dict)
                    if not BTRollLists_Staging.objects.filter(id=i_dict['id']).exists():
                        BTRollLists_Staging.objects.create(**i_dict)
                    else:
                        i_dict.pop('id')
                        BTRollLists_Staging.objects.create(**i_dict)
                for i in not_registered:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTNotRegistered.objects.create(**i_dict)
                for i in total_regs:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTStudentRegistrations.objects.create(**i_dict)
                    if not BTStudentRegistrations_Staging.objects.filter(id=i_dict['id']).exists():
                        BTStudentRegistrations_Staging.objects.create(**i_dict)
                    else:
                        i_dict.pop('id')
                        BTStudentRegistrations_Staging.objects.create(**i_dict)
                for i in dropped_regular:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTDroppedRegularCourses.objects.create(**i_dict)
                for i in marks:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    BTMarks.objects.create(**i_dict)
                    if not BTMarks_Staging.objects.filter(id=i_dict['id']).exists():
                        BTMarks_Staging.objects.create(**i_dict)
                    else:
                        i_dict.pop('id')
                        BTMarks_Staging.objects.create(**i_dict)
                for i in grades:
                    i_dict = i.__dict__
                    i_dict.pop('_state')
                    i_dict['RegId_id'] = i_dict['RegId']
                    i_dict.pop('RegId')
                    BTStudentGrades.objects.create(**i_dict)
                    if not BTStudentGrades_Staging.objects.filter(id=i_dict['id']).exists():
                        BTStudentGrades_Staging.objects.create(**i_dict)
                    else:
                        i_dict.pop('id')
                        BTStudentGrades_Staging.objects.create(**i_dict)
                # BTRollLists_Staging.objects.filter(student__RegNo=student_obj.RegNo, RegEventId__BSem=1, RegEventId__BYear=np.BYear, RegEventId__Regulation=np.Regulation).delete()
                # BTStudentRegistrations_Staging.objects.filter(sub_id_id__in=subjects.values_list('id', flat=True), student__student__RegNo=student_obj.RegNo).delete()
                # BTMarks_Staging.objects.filter(Registration_id__in=total_regs.values_list('id', flat=True)).delete()
                # BTStudentGrades_Staging.objects.filter(RegId_id__in=total_regs.values_list('id', flat=True)).delete()
                rolls.delete()
                total_regs.delete()
                marks.delete()
                grades.delete()
                not_registered.delete()
                dropped_regular.delete()
    return "Completed!!!"