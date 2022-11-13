from ADAUGDB.models import BTMarksDistribution
import copy

def get_course_structure_file(file):
    import pandas as pd
    file = pd.read_excel(file)
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
        if ncolumns == 4: dis_names = 'Minor-I'+','+'MID'+','+'Minor-II'+','+'END'
        elif ncolumns == 2: dis_names = 'Internal'+','+'External'
        mark_dis_row = (row['Regulation'], t_marks, dis_names, mark_dis.PromoteThreshold)
        if mark_dis_row not in mark_dis_rows:
            mark_dis_rows.append(mark_dis_row)
        row['MarkDistribution_id'] = mark_dis_rows.index(mark_dis_row)+1
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
        row['CourseStructure_id'] = cs_file.loc[(cs_file['BYear']==row['BYear']) & (cs_file['BSem']==row['BSem']) & (cs_file['Dept']==row['Dept']) & \
            (cs_file['Regulation']==row['Regulation']) & (cs_file['Category']==row['Category']) & (cs_file['Type']==row['Type']) & \
                (cs_file['Creditable']==row['Creditable']) & (cs_file['Credits']==row['Credits'])].index
    course_data = file[['SubCode', 'SubName', 'OfferedBy', 'CourseStructure_id', 'lectures', 'tutorials', 'practicals', 'DistributionRatio', 'MarkDistribution_id']]
    course_data.index = course_data.index + 1
    course_data.index.name = 'id'
    print(course_data)
    subjects_data = []
    for _, row in org_file.iterrows():
        new_row = [row['id'], row['RegEventId_id']]
        cs_id = cs_file.loc[(cs_file['BYear']==row['BYear']) & (cs_file['BSem']==row['BSem']) & (cs_file['Dept']==row['Dept']) & \
            (cs_file['Regulation']==row['Regulation']) & (cs_file['Category']==row['Category']) & (cs_file['Type']==row['Type']) & \
                (cs_file['Creditable']==row['Creditable']) & (cs_file['Credits']==row['Credits'])].index
        course_id = course_data.loc[(course_data['SubCode']==row['SubCode']) & (course_data['SubName']==row['SubName']) & (course_data['OfferedBy']==row['OfferedBy'])&\
            (course_data['CourseStructure_id']==cs_id)].index
        new_row.append(course_id)
    subjects_frame = pd.DataFrame(subjects_data, columns=['id', 'RegEventId_id', 'course_id'])
    print(subjects_frame)
        
    mark_dis_dataset.to_excel(r"C:\Users\sasib\Desktop\db\btech\MarkDistribution.xlsx")
    cs_file.to_excel(r"C:\Users\sasib\Desktop\db\btech\sampledb\course_structure.xlsx")
    course_data.to_excel(r"C:\Users\sasib\Desktop\db\btech\sampledb\courses.xlsx")
    subjects_frame.to_excel(r"C:\Users\sasib\Desktop\db\btech\sampledb\subjects.xlsx", index=False)
# get_course_structure_file(r"C:\Users\sasib\Desktop\db\btech\phy_Subjects.xlsx")