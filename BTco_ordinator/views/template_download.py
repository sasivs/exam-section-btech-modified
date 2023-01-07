from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from django.http import HttpResponse
from ADAUGDB.user_access_test import template_download_access 
from BThod.models import BTCoordinator, BTFaculty_user
from BTco_ordinator.forms import TemplateDownloadForm, BTFacultyAssignment
from BTco_ordinator.models import BTSubjects, BTRegistrationDetails, BTSubjectInfo
from ADAUGDB.models import BTRegistrationStatus
from ADAUGDB.constants import DEPARTMENTS, YEARS, SEMS, REGULATIONS
import pandas as pd
import numpy as np
import xlsxwriter
from django.db import connection
from django.db.models import Q

@login_required(login_url="/login/")
@user_passes_test(template_download_access)
def download_template(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    if 'Co-ordinator' in groups:
        current_user = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        current_user.group = 'Co-ordinator'
    elif 'Faculty' in groups:
        current_user = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True)
        current_user.group = 'Faculty'
    if request.method == 'POST':
        form = TemplateDownloadForm(current_user, request.POST)
        if request.POST.get('submit-form'):
            if form.is_valid():
                if current_user.group == 'Co-ordinator':
                    event = BTRegistrationStatus.objects.filter(id=form.cleaned_data.get('regID')).first()
                    if event.Mode == 'R':
                        if int(form.cleaned_data.get('option')) == 1:
                            filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-'+event.Mode
                        elif int(form.cleaned_data.get('option')) == 2:
                            filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-Open-'+event.Mode
                        elif int(form.cleaned_data.get('option')) == 3:
                            filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-MDC-'+event.Mode
                        workbook = generate_template(event.AYear, event.ASem, event.BYear, event.BSem, event.Dept, event.Mode, event.Regulation, int(form.cleaned_data.get('option')), response)
                    elif event.Mode == 'B':
                        if form.cleaned_data.get('option').split('-')[-1] == 'Exam':
                            option = int(form.cleaned_data.get('option').split('-')[0])
                            if option == 1:
                                filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-'+event.Mode + '-' + 'Exam'
                            elif option == 2:
                                filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-Open-'+event.Mode + '-' + 'Exam'
                            elif option == 3:
                                filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-MDC-'+event.Mode +'-' + 'Exam'

                            workbook = generate_exam_finalized_template(event.AYear, event.ASem, event.BYear, event.BSem, event.Dept, event.Mode, event.Regulation, option, response)
                        else:
                            if int(form.cleaned_data.get('option')) == 1:
                                filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-'+event.Mode + '-' + 'Study'
                            elif int(form.cleaned_data.get('option')) == 2:
                                filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-Open-'+event.Mode + '-' + 'Study'
                            elif int(form.cleaned_data.get('option')) == 3:
                                filename = DEPARTMENTS[event.Dept-1]+'-'+YEARS[event.BYear]+'-Sem-'+SEMS[event.ASem]+'-'+REGULATIONS[event.Regulation]+'-MDC-'+event.Mode + '-' + 'Study'

                            workbook = generate_template(event.AYear, event.ASem, event.BYear, event.BSem, event.Dept, event.Mode, event.Regulation, int(form.cleaned_data.get('option')), response)

                    response['Content-Disposition'] = 'attachment; filename={regevent}.xlsx'.format(regevent=filename)
                    return response
                elif current_user.group == 'Faculty':
                    rom2int = {'I':1,'II':2,'III':3,'IV':4}
                    regid = form.cleaned_data.get('regID').split(',')[0]
                    subject = form.cleaned_data.get('regID').split(',')[1]
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
                    if regid.startswith('SC'):
                        strs = regid.split(':')
                        ayear = int(strs[2])
                        asem = int(strs[3])
                        byear = rom2int[strs[0]]
                        bsem = rom2int[strs[1]]
                        regulation = float(strs[4])
                        mode = strs[5]
                        depts = BTFacultyAssignment.objects.filter(Coordinator_id=current_user.Faculty_id, RegEventId__Status=1, Subject__course__SubCode=subject,\
                            RegEventId__AYear=ayear, RegEventId__ASem=asem, RegEventId__BYear=byear, RegEventId__BSem=bsem, RegEventId__Regulation=regulation, RegEventId__Mode=mode).\
                            values_list('RegEventId__Dept', flat=True)
                    else:
                        depts = BTFacultyAssignment.objects.filter(Coordinator_id=current_user.Faculty_id, RegEventId__Status=1, Subject__course__SubCode=subject,\
                            RegEventId_id=regid)
                        event_obj = depts.first().RegEventId
                        depts = depts.values_list('RegEventId__Dept', flat=True)
                        mode = event_obj.Mode
                        ayear = event_obj.AYear
                        byear = event_obj.BYear
                        bsem = event_obj.BSem
                        asem = event_obj.ASem
                        regulation = event_obj.Regulation
                    response['Content-Disposition'] = 'attachment; filename=Template({regevent}).xlsx'.format(regevent=filename)
                    if mode == 'R':
                        filename = subject + '-' + DEPARTMENTS[event_obj.Dept-1] + '-' + YEARS[event_obj.BYear] + '-Sem-' + SEMS[event_obj.BSem] + '-' + REGULATIONS[event_obj.Regulation] + '-' + event_obj.Mode
                        workbook = generate_subject_wise_grade_report(ayear, asem, byear, bsem, mode, regulation, subject, depts, response)
                    elif mode == "B":
                        if not request.POST.get('backlog-faculty'):
                            return render(request, 'BTco_ordinator/TemplateDownload.html', {'form':form})
                        else:
                            if form.cleaned_data.get('option') == 'Exam':
                                filename = subject + '-' + DEPARTMENTS[event_obj.Dept-1] + '-' + YEARS[event_obj.BYear] + '-Sem-' + SEMS[event_obj.BSem] + '-' + REGULATIONS[event_obj.Regulation] + '-' + event_obj.Mode + '-' + 'Exam'
                                workbook = generate_backlog_subject_wise_grade_report(ayear, asem, byear, bsem, mode, regulation, subject,depts,response)
                            else:
                                filename = subject + '-' + DEPARTMENTS[event_obj.Dept-1] + '-' + YEARS[event_obj.BYear] + '-Sem-' + SEMS[event_obj.BSem] + '-' + REGULATIONS[event_obj.Regulation] + '-' + event_obj.Mode + '-' + 'Study'
                                workbook = generate_subject_wise_grade_report(ayear,asem,byear,bsem,mode,regulation,subject,depts,response)                   
                    response['Content-Disposition'] = 'attachment; filename={regevent}.xlsx'.format(regevent=filename)
                    return response
    else:
        form = TemplateDownloadForm(current_user)
    return render(request, 'BTco_ordinator/TemplateDownload.html', {'form':form})


def getFormats(workbook, flag):
    formats = {}
    t1 = workbook.add_format()
    t1.set_bold()
    t1.set_align('center')
    t1.set_font_size(18)
    t1.set_font_name('Times New Roman')
    
    formats['t1'] = t1
    t2 = workbook.add_format()
    t2.set_bold()
    t2.set_align('center')
    t2.set_font_size(14)
    t2.set_font_name('Times New Roman')
    formats['t2'] = t2
    f2 = workbook.add_format()
    f2.set_bold()
    f2.set_align('center')
    f2.set_border()
    f2.set_font_name('Times New Roman')
    formats['f2'] = f2
    fb = workbook.add_format()
    fb.set_bold()
    fb.set_border()
    fb.set_text_wrap()
    fb.set_font_name('Times New Roman')
    formats['fb'] = fb
    fwb = workbook.add_format()
    # fwb.set_bold()
    fwb.set_border()
    fwb.set_text_wrap()
    fwb.set_align('left')
    fwb.set_font_name('Times New Roman')
    formats['fwb'] = fwb
    fbbc = workbook.add_format()
    fbbc.set_bold()
    fbbc.set_border()
    fbbc.set_align('center')
    fbbc.set_font_name('Times New Roman')
    formats['fbbc'] = fbbc
    fbc = workbook.add_format()
    fbc.set_bold()
    fbc.set_align('center')
    fbc.set_font_name('Times New Roman')
    formats['fbc'] = fbc
    fbl = workbook.add_format()
    fbl.set_bold()
    fbl.set_align('left')
    fbl.set_font_name('Times New Roman')
    formats['fbl'] = fbl
    fbr = workbook.add_format()
    fbr.set_bold()
    fbr.set_border()
    fbr.set_align('right')
    fbr.set_font_name('Times New Roman')
    formats['fbr'] = fbr
    fl = workbook.add_format()
    fl.set_align('left')
    fl.set_border()
    fl.set_font_name('Times New Roman')
    formats['fl'] = fl
    fr = workbook.add_format()
    fr.set_align('right')
    fr.set_border()
    fr.set_font_name('Times New Roman')
    formats['fr'] = fr
    fc = workbook.add_format()
    fc.set_align('center')
    fc.set_border()
    fc.set_font_name('Times New Roman')
    formats['fc'] = fc
    fp = workbook.add_format()
    fp.set_align('center')
    fp.set_border()
    fp.set_font_name('Times New Roman')
    fp.set_num_format('0.00%')
    formats['fp'] = fp
    f1 = workbook.add_format()
    
    formats['f1'] = f1
    fsummary = workbook.add_format()
    fsummary.set_align('center')
    fsummary.set_border()
    fsummary.set_font_name('Times New Roman')
    fsummary.set_bold()
    fsummary.set_font_size(20)
    fsummary.set_valign('vcenter')
    formats['fsummary']  = fsummary
    for k in formats.keys():
        formats[k].set_locked(flag)
    prgrade = workbook.add_format()
    prgrade.set_align('center')
    prgrade.set_border()
    prgrade.set_font_name('Times New Roman')
    prgrade.set_locked(True)
    prgrade.set_bg_color('yellow')
    formats['prgrade'] = prgrade

    return formats

def generate_template(ayear,asem,byear,bsem,dept,mode,regulation,flag, response):
    eventCols = ['AYear','ASem','BYear','BSem','Dept','Regulation','Mode','SubCode']
    grades = {1:['EX','A','B','C','D','P','F','R','I','X','W'],
          2: ['S','A','B','C','D','E','P','F','R','I','X','W'], 
          3:['EX','A','B','C','D','P','F','R','I','X','W'], 
          4:['EX','A','B','C','D','P','F','R','I','X','W']}
    passGrades = ['EX','A','B','C','D','E','P','S']
    alphas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
          'W', 'X', 'Y', 'Z']
    Years = ['I', 'II', 'III', 'IV']
    itor = {1:'I',2:'II',3:'III',4:'IV'}
    month2num={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','June':'06','July':'07',
            'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    deptstrs = ['BioTechnology', 'Chemical Engineering', 'Civil Engineering', 'Computer Science and Engineering',
         'Electrical Engineering', 'Electronics and Communications Engineering', 'Mechanical Engineering',
         'Metallurgical and Materials Engineering']
    height = 30
    notSubmitted = []
    headerStr = ''
    rmode = 1
    rmodeStr = ''
    if(mode=='B'):
        rmodeStr = '-Study'
        headerStr = ' Backlog Study'
    if(BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Dept=dept,Mode=mode,Regulation=regulation,RMode=rmode).exists()):
        cursor = connection.cursor()
        cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Dept"={} and "Mode"=\'{}\' and "Regulation"={} and "RMode"={}'.format(ayear,asem,byear,bsem,dept,mode,regulation,rmode))
        registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Dept=dept,Mode=mode,Regulation=regulation,RMode=rmode)
        markDetails = pd.DataFrame(cursor.fetchall())
        if(flag==1):
            registrations = registrations.filter(~Q(Category='OPC')).filter(~Q(Category='OEC'))
            if((byear==4) or (byear==3)):
                registrations = registrations.filter(~Q(Category='MDC'))
            optSuffix = ''
        elif(flag==2):
            registrations = registrations.filter(Category='OPC')
            optSuffix = '-Open'
        elif(flag==3):
            if(byear==3 or byear==4):
                registrations = registrations.filter(Category='MDC')
                optSuffix = '-MDC'
            else:
                return 
        
        markDetails.columns = ['id','AYear','ASem','BYear','BSem','Regulation','Dept','RegEventId','Mode','SubId','SubCode','RMode','Distribution','DistributionNames','DistributionRatio','RegNo','RollNo','Name','Marks','TotalMarks','Registration_id']
        cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Dept"={} and "Mode"=\'{}\' and "Regulation"={} and "RMode"={}'.format(ayear,asem,byear,bsem,dept,mode,regulation,rmode))
        gradeDetails = pd.DataFrame(cursor.fetchall(),columns=['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','RMode','Grade'])
        cursor.execute('Select * from "BTGradeThresholdDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Dept"={} and "Mode"=\'{}\' and "Regulation"={}'.format(ayear,asem,byear,bsem,dept,mode,regulation))
        gradeThresholdDetails = pd.DataFrame(cursor.fetchall(),columns =['id','AYear','ASem','BYear','BSem','Regulation','Mode','Dept','RegEventId','SubCode','G1','G2','G3','G4','G5','G6','G7','ET'] )
        if(registrations.count()!=0):
            print(registrations.count())
            print(str(dept)+'-'+str(byear))
            workbook = xlsxwriter.Workbook(response, {'in_memory':True})
            subjects = pd.DataFrame.from_records(registrations.values('sub_id','SubCode','SubName','Credits','Category','HeldInMonth','HeldInYear','Dept',)) 
            subjects = subjects.drop_duplicates(subset=['SubCode'],keep='first')
            subjectList = subjects['SubCode'].drop_duplicates().to_list()
            print(subjectList)
            markDetails = markDetails[markDetails['SubCode'].isin(subjectList)]
            gradeDetails = gradeDetails[gradeDetails['SubCode'].isin(subjectList)]
            gradeThresholdDetails = gradeThresholdDetails[gradeThresholdDetails['SubCode'].isin(subjectList)]
            N = 0
            noconsolidated = False
            for si, subject in subjects.iterrows():
                tl = False
                subjectObj = BTSubjects.objects.get(id=subject['sub_id'])
                
                subRegistrations = pd.DataFrame.from_records(registrations.filter(SubCode=subject['SubCode']).values())
                subMarkDetails = markDetails[markDetails['SubCode']==subject['SubCode']]
                subGradeDetails = gradeDetails[gradeDetails['SubCode']==subject['SubCode']]
                subGradeThresholdDetails = gradeThresholdDetails[gradeThresholdDetails['SubCode']==subject['SubCode']]
                print(subGradeThresholdDetails.shape)
                if(subGradeThresholdDetails.shape[0]==0 or subGradeDetails.shape[0]==0):
                    noconsolidated = True
                    notSubmitted.append(subject['SubCode'])
                    continue 

                if(subjectObj.OfferedBy!=dept):
                    continue
                
                subThresholds = {}
                for gIndex, g in enumerate(grades[regulation]):
                    if(g=='F'):
                        break
                    subThresholds[g] = subGradeThresholdDetails.iloc[0,10+gIndex]
                gradeStats = subGradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)
                for g in grades[regulation]:
                    if(not (g in gradeStats.columns)):
                        gradeStats.loc[:,g]=0
                # For subjects which are common avg, std, max should be the stats for all students
                gradeStats = gradeStats[grades[regulation]]
                resGrades = pd.merge(subMarkDetails,subGradeDetails, on=['RegNo']+eventCols )
                resGrades.loc[:, 'Result'] = resGrades['Grade'].apply(lambda x: 'P' if(x in passGrades) else x)
                resGrades = resGrades[resGrades['Result']=='P']
                if(resGrades.shape[0]==0):
                    std = 0
                    avg = 0
                    max = 0
                else:    
                    std = np.round(resGrades['TotalMarks'].std(),2)
                    avg = np.round(resGrades['TotalMarks'].mean(),2)
                    max = resGrades['TotalMarks'].max()
                    if(np.isnan(std)):
                        std = 0.0
                subRegistrations.sort_values(by=['RollNo'],inplace=True)
                print(subject['SubCode'])
                worksheet = workbook.add_worksheet(subject['SubCode'])
                worksheet.protect()

                # Setting the title Rows
                formats = getFormats(workbook, False)
                colWidths = [8, 10,10,40,8,8,8,8,8,12,8,8]
                for colIndex in range(len(colWidths)):
                    worksheet.set_column(alphas[colIndex]+':'+alphas[colIndex], colWidths[colIndex], formats['f1'])  # S.NO
                worksheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                
                worksheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+' Semester AY-'+ str(ayear)+'-'+str(ayear+1) , formats['t2'])
                worksheet.merge_range('A4:M4', 'Subject Code: ' + str(subject['SubCode'])+ ' Subject Name: ' + 
                    subject['SubName'] + ' Credits: ' + str(subject['Credits']) + headerStr  , formats['t2'])
                startRowIndexZ = 5

                # Setting the Header Row
                worksheet.set_row(startRowIndexZ, height)
                headerCols = ['S.No','RegNo','RollNo','Name','MM/YY']
                for hIndex in range(len(headerCols)):
                    worksheet.write(startRowIndexZ, hIndex, headerCols[hIndex], formats['fb'])
                
                md = subjectObj.MarkDistribution
                print(md.Distribution)
                print(subjectObj.DistributionRatio)
                if(',' in md.Distribution):
                    print(md.Distribution)
                    tl = True
                    dists = md.Distribution.split(',')
                    mcols = dists[0].split('+') + dists[1].split('+') 
                    distnames = md.DistributionNames.split(',')
                    mnames = distnames[0].split('+')  +distnames[1].split('+') 
                else:
                    tl = False
                    mcols = md.Distribution.split('+')
                    mnames = md.DistributionNames.split('+')
                numMarkCols = len(mcols)
                marksColSIndexZ = 5 
                totalColIndexZ = marksColSIndexZ + numMarkCols 
                mcolIndex = 0
                for mcol,mname in zip(mcols,mnames):
                    worksheet.write(startRowIndexZ, marksColSIndexZ+mcolIndex, mname+'('+mcol+')', formats['fbbc'])
                    mcolIndex+=1

                worksheet.write(startRowIndexZ, totalColIndexZ, 'Total(100)', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 1, 'Result', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 2, 'Grade', formats['fb'])
                studentStartRowIndexZ = 6
                stIndex = 0
                N_sub = subRegistrations.shape[0]
                if (N == 0):
                    df_p = subRegistrations
                    N = N_sub
                else:
                    df_p = pd.concat([df_p, subRegistrations]).drop_duplicates(subset='RegNo', keep='last')
                studentEndRowIndexZ = studentStartRowIndexZ + N_sub -1
                gtRowIndexZ =  studentEndRowIndexZ+4
                for gIndex, g in enumerate(grades[regulation]):
                    worksheet.write(gtRowIndexZ + gIndex, 0, g , formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex, 2, gradeStats.iloc[0][g],formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex,3, round(100*gradeStats.iloc[0][g]/N_sub,2))
                    if(gIndex<len(subThresholds)): #gIndex is before Index upto P grade
                        worksheet.write(gtRowIndexZ + gIndex, 1,subThresholds[g] , formats['fb'])
                
                chart = workbook.add_chart({'type':'line'})
                chart.add_series({
                    'categories': '='+subject['SubCode']+'!$A'+str(gtRowIndexZ+1)+':$A'+ str(len(subThresholds) +gtRowIndexZ),
                    'values':'='+subject['SubCode']+'!$C'+str(gtRowIndexZ+1)+':$C'+ str(len(subThresholds) +gtRowIndexZ),
                    'smooth':True,
                    'marker': {'type': 'circle'},
                    'data_labels': {'value': True},
                })
                chart.set_title({'name': 'Grade Distribution'})
                chart.set_x_axis({'name':'Grades'})
                chart.set_y_axis({'name': 'Count'})
                chart.set_style(11)

                worksheet.insert_chart('G'+str(gtRowIndexZ+4), chart,{'x_offset':20, 'y_offset':5})

                totalRowIndexZ = gtRowIndexZ + len(grades[regulation])    
                # Write the header row for Grade Threshold Count Percentage Box
                for gIndex, gval in enumerate(['Grade','Threshold','Count','Percentage']):
                    worksheet.write(gtRowIndexZ-1, gIndex, gval, formats['fb'])
                
                # Total summing the number of students accounted in the grade threshold Counts
                worksheet.write(totalRowIndexZ, 0, 'Total', formats['fb'])
                worksheet.write(totalRowIndexZ, 2, N_sub, formats['fb'])
                # Stats to be printed under total marks column towards the bottom
                stath = ['Class Average=','SD=','MAX=']

                stats = [avg,std,max]
                
                print(stats)
                for statIndex in range(3):
                    worksheet.write(studentEndRowIndexZ + 2 + statIndex, totalColIndexZ-1, stath[statIndex])
                    worksheet.write(studentEndRowIndexZ + 2 +statIndex, totalColIndexZ,stats[statIndex])
                subRegistrations = subRegistrations.reset_index()
                subRegistrations = subRegistrations.sort_values(by=['RollNo'])
                for sti, strow in subRegistrations.iterrows():
                    studentMarksRow = subMarkDetails[subMarkDetails['RegNo']==strow['RegNo']].iloc[0]
                    studentGradeRow = subGradeDetails[subGradeDetails['RegNo']==strow['RegNo']].iloc[0]
                    if(tl):
                        studentMarks = studentMarksRow['Marks'].split(',')[0].split('+') + studentMarksRow['Marks'].split(',')[1].split('+')
                    else:
                        studentMarks = studentMarksRow['Marks'].split('+')
                    studentMarks = [float(i) for i in studentMarks]
                    stDataRow = [sti + 1,strow['RegNo'],strow['RollNo'],strow['Name'],
                        month2num[strow['HeldInMonth']]+'-'+str(strow['HeldInYear']%100)]
                    stDataRowFormats = [formats['fc'],formats['fc'],formats['fc'],formats['fl'],formats['fc']]
                    for mIndex in range(len(mcols)):
                        stDataRow.append(studentMarks[mIndex])
                        stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentMarksRow['TotalMarks'])
                    stDataRowFormats.append(formats['fc'])

                    
                    if(studentGradeRow['Grade'] in passGrades):
                        stDataRow.append('P')
                    else:
                        stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    strowIndexZ = studentStartRowIndexZ + sti 
                    
                    for stdIndex in range(len(stDataRow)):
                        worksheet.write(strowIndexZ, stdIndex,stDataRow[stdIndex],stDataRowFormats[stdIndex])
                    
                    stIndex = stIndex + 1
            if(not noconsolidated):
                df_p = pd.DataFrame(registrations.values('RegNo','RollNo','Name')).drop_duplicates(subset='RegNo', keep='last')
                N = df_p.shape[0]
                worksheet = workbook.add_worksheet('Consolidated')
                start = 6
                formats = getFormats(workbook, False)
                
                worksheet.set_column('A:A', 8, formats['f1'])  # S.NO
                worksheet.set_column('B:B', 10, formats['f1'])  # RegNo
                worksheet.set_column('C:C', 10, formats['f1'])  # RollNo
                worksheet.set_column('D:D', 40, formats['f1'])  # Name
                
                worksheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                worksheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+ ' Semester AY-'+str(ayear)+'-'+str(ayear+1) + headerStr, formats['t2'])
                consolidatedHeader = ['S.No', 'RegNo', 'RollNo', 'Name'] +subjectList
                for sub in range(len(consolidatedHeader)):
                    worksheet.write(start - 1, sub, consolidatedHeader[sub], formats['fb'])
                
                stIndex = 0
                for stInd, student in df_p.iterrows():
                    studRow = [stIndex + 1,student['RegNo'],student['RollNo'],student['Name']]
                    studFormats = [formats['fc'],formats['fc'],formats['fc'],formats['fl']]
                    for stdi in range(len(studRow)):
                        worksheet.write(start + stIndex, stdi, studRow[stdi], studFormats[stdi])
                    studentGradeDetails = gradeDetails[gradeDetails['RegNo']==student['RegNo']]
                    for sub in range(len(subjectList)):
                        studentSubGradeDetails = studentGradeDetails[studentGradeDetails['SubCode']==subjectList[sub]]
                        studentGrade = ''
                        if(studentSubGradeDetails.shape[0]>0):
                            studentGrade = studentSubGradeDetails.iloc[0].Grade
                        worksheet.write(start + stIndex, sub+4,studentGrade,formats['fc'])
                    stIndex += 1
                endIndex = start + df_p.shape[0]
                for gIndex, g in enumerate(grades[regulation]):
                    worksheet.write(endIndex + 3+ gIndex, 3, g, formats['fbr'])
                
                for sub in range(4, 4 + len(subjectList)):
                    subGradeDetails = gradeDetails[gradeDetails['SubCode']==subjectList[sub-4]]
                    gradeStats = subGradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)

                    subEndIndex = start + subGradeDetails.shape[0]
                    for gIndex,g in enumerate(grades[regulation]):
                        if(not (g in gradeStats.columns)):
                            gradeStats.loc[:,g]=0
                        worksheet.write(endIndex + 3+ gIndex, sub, gradeStats.iloc[0][g], formats['fc'])
                    worksheet.write(endIndex + 3+ gIndex+1,sub,subGradeDetails.shape[0],formats['fc'])
                if(flag!=2): # No summary for open electives 
                    summarysheet = workbook.add_worksheet('Summary')
                    numSummaryCols = 4 + len(grades[regulation])-3
                    for ci in range(numSummaryCols):
                        cw = 9
                        if(ci==1):
                            cw = 40
                        summarysheet.set_column(alphas[ci]+':'+alphas[ci],cw, formats['fl'])  # S.NO
                    summarysheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                    summarysheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+ ' Semester AY-'+str(ayear)+'-'+str(ayear+1) + headerStr, formats['t2'])
                    summarysheet.merge_range('A4:M4', 'Department of ' + deptstrs[dept-1], formats['t2'])
                    summarysheet.write(start - 2, 10, 'Date:', formats['fb'])
                    summaryCols = ['S.No','Subject Name','Credits'] + grades[regulation][:-3] + ['Others(R,I,X,W)','Total']
                    for ci,sc in enumerate(summaryCols):
                        summarysheet.write(start - 1, ci, sc, formats['fb'])
                    subPrintIndex = 1
                    print('Summary')
                    subIndex = 0 
                    for si, subject in subjects.iterrows():
                        print(subject['SubCode']+'::'+str(subIndex))
                        subjectObj = BTSubjects.objects.get(id=subject['sub_id'])
                        subInfoList = BTSubjectInfo.objects.filter(AYear=ayear, ASem=asem, BYear=byear,BSem=bsem, Regulation=regulation, SubCode=subject['SubCode'],OfferedBy=subjectObj.OfferedBy)
                        if(subInfoList.count()>1):
                            print('Common Subject' + subject['SubCode']+'::'+str(subIndex))
                            continue
                        subGradeDetails = gradeDetails[gradeDetails['SubCode']==subject['SubCode']]
                        subMarkDetails = markDetails[markDetails['SubCode']==subject['SubCode']]
                        subGradeThresholdDetails = gradeThresholdDetails[gradeThresholdDetails['SubCode']==subject['SubCode']]
                        summarysheet.set_row(start - 1 + subPrintIndex * 2 - 1, 50)
                        summarysheet.write(start - 1 + subPrintIndex * 2 - 1, 0, subPrintIndex, formats['fsummary'])
                        # if(subInfoList.count()>1): # This subject is common for multiple departments so avg, std should be calculated accordingly
                        #     cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Mode"=\'{}\' and "Regulation"={} and "SubCode"=\'{}\''.format(ayear,asem,byear,bsem,mode,regulation,subject['SubCode']))
                        #     allMarks = pd.DataFrame(cursor.fetchall(),columns=markDetails.columns)
                        #     cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Mode"=\'{}\' and "Regulation"={} and "SubCode"=\'{}\''.format(ayear,asem,byear,bsem,mode,regulation,subject['SubCode']))
                        #     allGrades = pd.DataFrame(cursor.fetchall(),columns=gradeDetails.columns)
                        #     resGrades = pd.merge(allMarks,allGrades, on=['RegNo']+eventCols )
                        # else:
                        resGrades = pd.merge(subMarkDetails,subGradeDetails, on=['RegNo']+eventCols )
                        resGrades.loc[:, 'Result'] = resGrades['Grade'].apply(lambda x: 'P' if(x in passGrades) else x)
                        resGrades = resGrades[resGrades['Result']=='P']
                        std = resGrades['TotalMarks'].std()
                        avg = resGrades['TotalMarks'].mean()
                        max = resGrades['TotalMarks'].max()
                        std = round(std,2)
                        avg = round(avg,2)
                        summarysheet.write(start - 1 + subPrintIndex * 2 - 1, 1,  subject['SubCode'] 
                                        + '\n' + subject['SubName'] 
                                        + '\n (AVG:' + str(avg)  
                                        + 'SD:' + str(std) 
                                        + '), MAX MARKS:' 
                                        + str(max),
                                        formats['fwb'])
                        gradeStats = subGradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)

                        for gIndex,g in enumerate(grades[regulation]):
                            if(not (g in gradeStats.columns)):
                                gradeStats.loc[:,g]=0
                        gradeStats.loc[:,'Others'] = gradeStats.loc[:,'I'] + gradeStats.loc[:,'X']  + gradeStats.loc[:,'W']
                        gradeStats = gradeStats[grades[regulation][:-3]+['Others']]        
                        gradeStats.index = [0]
                        print(gradeStats)
                        summarysheet.write(start - 1 + subPrintIndex * 2 - 1, 2, subject['Credits'], formats['fc'])
                        for col, g in enumerate(list(gradeStats.columns)):
                            summarysheet.write(start - 1 + subPrintIndex * 2 - 1, col+3, gradeStats.loc[0,g], formats['fsummary'])  # all grades
                        summarysheet.write(start - 1 + subPrintIndex * 2 - 1, numSummaryCols, subGradeDetails.shape[0],formats['fsummary'])
                        summarysheet.set_row(start - 1 + subPrintIndex * 2, 13)
                        summarysheet.write(start - 1 + subPrintIndex * 2, 1, '(Limits)', formats['fr'])
                        limitCols = ['>=' + str(int(subGradeThresholdDetails.iloc[0]['G1']))]
                        for i in range(2,grades[regulation].index('F')+1): 
                            limitCols = limitCols + ['(' + str(int(subGradeThresholdDetails.iloc[0]['G'+str(i)])) + '-' +  str(int(subGradeThresholdDetails.iloc[0]['G'+str(i-1)])-1) + ')']
                        limitCols = limitCols + ['<' + str(int(subGradeThresholdDetails.iloc[0]['G'+str(grades[regulation].index('F'))])) ]    
                        for li, lcol in enumerate(limitCols):
                            summarysheet.write(start - 1 + subPrintIndex * 2, 3+li,lcol , formats['fc'])
                        subPrintIndex = subPrintIndex + 1
                        subIndex +=1
            else:
                print(str(dept) + '-' + str(byear) + '-Not Submitted ' + ','.join(notSubmitted))
            workbook.close()



def generate_subject_wise_grade_report(ayear,asem,byear, bsem, mode, regulation, subcode,depts, response):
    bchs = ['BTE', 'CHE', 'CE', 'CSE', 'EEE', 'ECE', 'ME', 'MME', 'Chemistry', 'Physics']
    Years = ['I', 'II', 'III', 'IV']
    alphas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
            'W', 'X', 'Y', 'Z']
    eventCols = ['AYear','ASem','BYear','BSem','Dept','Regulation','Mode','SubCode']
    passGrades = ['EX','A','B','C','D','E','P','S']
    grades = {1:['EX','A','B','C','D','P','F','R','I','X','W'],
            2: ['S','A','B','C','D','E','P','F','R','I','X','W'], 
            3:['EX','A','B','C','D','P','F','R','I','X','W'], 
            4:['EX','A','B','C','D','P','F','R','I','X','W']}
    itor = {1:'I',2:'II',3:'III',4:'IV'}
    month2num={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','June':'06','July':'07',
            'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    # if(mode!='R'):
    #     return 
    height = 30
    rmode = 1
    print(BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,RMode=rmode))
    if(BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,RMode=rmode).exists()):
        registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode, RMode=rmode)
        deptList = [depts]
        sheetNameList = [subcode]
        if(len(depts)>1):
            for dept in depts:
                deptList.append([dept])
                sheetNameList.append(subcode+'-'+bchs[dept-1])
        if mode == 'R':
            subjects = pd.DataFrame.from_records(BTSubjectInfo.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode).values())
        else:
            subids = registrations.distinct('sub_id').values_list('sub_id', flat=True)
            subjects = pd.DataFrame.from_records(BTSubjectInfo.objects.filter(SubId__in=subids).values())
        workbook = xlsxwriter.Workbook(response, {'in_memory':True})
        print(subcode)
        print(depts)
        for di, deptItem in enumerate(deptList):
            worksheet = workbook.add_worksheet(sheetNameList[di])
            worksheet.protect()
            if(len(deptItem)>1):
                registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,Dept__in=deptItem, RMode=rmode)
                cursor = connection.cursor()
                cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "RMode"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,rmode))
                markDetails = pd.DataFrame(cursor.fetchall())
                cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "RMode"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,rmode))
                gradeDetails = pd.DataFrame(cursor.fetchall(),columns=['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','Grade'])
                # gradeDetails = gradeDetails[['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','Grade']]
                cursor.execute('Select * from "BTGradeThresholdDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation))
                gradeThresholdDetails = pd.DataFrame(cursor.fetchall(),columns =['id','AYear','ASem','BYear','BSem','Regulation','Mode','Dept','RegEventId','SubCode','G1','G2','G3','G4','G5','G6','G7','ET'] )
                subject = subjects.iloc[0]
                markDetails.columns = ['id','AYear','ASem','BYear','BSem','Regulation','Dept','RegEventId','Mode','SubId','SubCode','RMode','Distribution','DistributionNames','DistributionRatio','RegNo','RollNo','Name','Marks','TotalMarks','Registration_id']
                resGrades = pd.merge(markDetails,gradeDetails, on=['RegNo']+eventCols )
                resGrades.loc[:, 'Result'] = resGrades['Grade'].apply(lambda x: 'P' if(x in passGrades) else x)
                resGrades = resGrades[resGrades['Result']=='P']
                print(resGrades.shape[0])
                if(resGrades.shape[0]==0):
                    std = 0
                    avg = 0
                    max = 0
                else:    
                    std = np.round(resGrades['TotalMarks'].std(),2)
                    avg = np.round(resGrades['TotalMarks'].mean(),2)
                    max = np.round(resGrades['TotalMarks'].max(),2)
                    if(np.isnan(std)):
                        std = 0.0
            else:
                registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,Dept=deptItem[0],  RMode=rmode)
                cursor = connection.cursor()
                cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "Dept"={} and "RMode"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,deptItem[0],rmode))
                markDetails = pd.DataFrame(cursor.fetchall())
                markDetails.columns = ['id','AYear','ASem','BYear','BSem','Regulation','Dept','RegEventId','Mode','SubId','SubCode','RMode','Distribution','DistributionNames','DistributionRatio','RegNo','RollNo','Name','Marks','TotalMarks','Registration_id']

                cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "Dept"={} and "RMode"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,deptItem[0],rmode))
                gradeDetails = pd.DataFrame(cursor.fetchall(),columns=['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','RMode', 'Grade'])
                # gradeDetails = gradeDetails[['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','Grade']]
                cursor.execute('Select * from "BTGradeThresholdDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "Dept"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,deptItem[0]))
                gradeThresholdDetails = pd.DataFrame(cursor.fetchall(),columns =['id','AYear','ASem','BYear','BSem','Regulation','Mode','Dept','RegEventId','SubCode','G1','G2','G3','G4','G5','G6','G7','ET'] )
                subject = subjects[subjects['Dept']==deptItem[0]].iloc[0]

                if(di>0): # for open electives and common subjects where department wise sheets are being prepared
                    # the average, sd, max values should be reused from the common grading sheet. So don't reset them
                    None
                else: # for service courses offered to single other department
                    resGrades = pd.merge(markDetails,gradeDetails, on=['RegNo']+eventCols )
                    resGrades.loc[:, 'Result'] = resGrades['Grade'].apply(lambda x: 'P' if(x in passGrades) else x)
                    resGrades = resGrades[resGrades['Result']=='P']
                    
                    if(resGrades.shape[0]==0):
                        std = 0
                        avg = 0
                        max = 0
                    else:    
                        std = round(resGrades['TotalMarks'].std(),2)
                        avg = round(resGrades['TotalMarks'].mean(),2)
                        max = resGrades['TotalMarks'].max()
                        if(np.isnan(std)):
                            std = 0.0
            if(registrations.count()!=0):

                print(registrations.count())
                registrations = pd.DataFrame.from_records(registrations.values())
                tl = False
                if(gradeThresholdDetails.shape[0]==0 or gradeDetails.shape[0]==0):
                    continue 
                subThresholds = {}
                for gIndex, g in enumerate(grades[regulation]):
                    if(g=='F'):
                        break
                    subThresholds[g] = gradeThresholdDetails.iloc[0,10+gIndex]
                gradeStats = gradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)
                for g in grades[regulation]:
                    if(not (g in gradeStats.columns)):
                        gradeStats.loc[:,g]=0
                gradeStats = gradeStats[grades[regulation]]
                registrations = registrations.sort_values(by='RollNo')
                
                # Setting the title Rows
                formats = getFormats(workbook, True)
                colWidths = [8, 10,10,40,8,8,8,8,8,12,8,8]
                for colIndex in range(len(colWidths)):
                    worksheet.set_column(alphas[colIndex]+':'+alphas[colIndex], colWidths[colIndex], formats['f1'])  # S.NO
                worksheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                
                worksheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+' Semester AY-'+ str(ayear)+'-'+str(ayear+1) , formats['t2'])
                worksheet.merge_range('A4:M4', 'Subject Code: ' + sheetNameList[di]+ ' Subject Name: ' + 
                    subject['SubName'] + ' Credits: ' + str(subject['Credits']), formats['t2'])
                startRowIndexZ = 5

                # Setting the Header Row
                worksheet.set_row(startRowIndexZ, height)
                headerCols = ['S.No','RegNo','RollNo','Name','MM/YY']
                for hIndex in range(len(headerCols)):
                    worksheet.write(startRowIndexZ, hIndex, headerCols[hIndex], formats['fb'])
                subjectObj = BTSubjects.objects.get(id=subject['SubId'])
                md = subjectObj.MarkDistribution
                print(md.Distribution)
                print(subjectObj.DistributionRatio)
                if(',' in md.Distribution):
                    print(md.Distribution)
                    tl = True
                    dists = md.Distribution.split(',')
                    mcols = dists[0].split('+') + dists[1].split('+') 
                    distnames = md.DistributionNames.split(',')
                    mnames = distnames[0].split('+')  +distnames[1].split('+') 
                else:
                    tl = False
                    mcols = md.Distribution.split('+')
                    mnames = md.DistributionNames.split('+')
                numMarkCols = len(mcols)
                marksColSIndexZ = 5 
                totalColIndexZ = marksColSIndexZ + numMarkCols 
                mcolIndex = 0
                for mcol,mname in zip(mcols,mnames):
                    worksheet.write(startRowIndexZ, marksColSIndexZ+mcolIndex, mname+'('+mcol+')', formats['fbbc'])
                    mcolIndex+=1
                worksheet.write(startRowIndexZ, totalColIndexZ, 'Total(100)', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 1, 'Result', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 2, 'Grade', formats['fb'])
                studentStartRowIndexZ = 6
                stIndex = 0
                N_sub = registrations.shape[0]
                studentEndRowIndexZ = studentStartRowIndexZ + N_sub -1
                gtRowIndexZ =  studentEndRowIndexZ+4
                for gIndex, g in enumerate(grades[regulation]):
                    worksheet.write(gtRowIndexZ + gIndex, 0, g , formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex, 2, gradeStats.iloc[0][g],formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex,3, round(100*gradeStats.iloc[0][g]/N_sub,2))
                    if(gIndex<len(subThresholds)): #gIndex is before Index upto P grade
                        worksheet.write(gtRowIndexZ + gIndex, 1,subThresholds[g] , formats['fb'])
                
                totalRowIndexZ = gtRowIndexZ + len(grades[regulation])    
                # Write the header row for Grade Threshold Count Percentage Box
                for gIndex, gval in enumerate(['Grade','Threshold','Count','Percentage']):
                    worksheet.write(gtRowIndexZ-1, gIndex, gval, formats['fb'])
                
                # Total summing the number of students accounted in the grade threshold Counts
                worksheet.write(totalRowIndexZ, 0, 'Total', formats['fb'])
                worksheet.write(totalRowIndexZ, 2, N_sub, formats['fb'])

                if(di==0):
                    chart = workbook.add_chart({'type':'line'})
                    chart.add_series({
                        'categories': '='+subject['SubCode']+'!$A'+str(gtRowIndexZ+1)+':$A'+ str(len(subThresholds) +gtRowIndexZ),
                        'values':'='+subject['SubCode']+'!$C'+str(gtRowIndexZ+1)+':$C'+ str(len(subThresholds) +gtRowIndexZ),
                        'smooth':True,
                        'marker': {'type': 'circle'},
                        'data_labels': {'value': True},
                    })
                    chart.set_title({'name': 'Grade Distribution'})
                    chart.set_x_axis({'name':'Grades'})
                    chart.set_y_axis({'name': 'Count'})
                    chart.set_style(11)

                    worksheet.insert_chart('G'+str(gtRowIndexZ+4), chart,{'x_offset':20, 'y_offset':5})
                # Stats to be printed under total marks column towards the bottom
                stath = ['Class Average=','SD=','MAX=']

                stats = [avg,std,max]
                
                print(stats)
                for statIndex in range(3):
                    worksheet.write(studentEndRowIndexZ + 2 + statIndex, totalColIndexZ-1, stath[statIndex])
                    worksheet.write(studentEndRowIndexZ + 2 +statIndex, totalColIndexZ,stats[statIndex])
                registrations = registrations.reset_index()
                registrations = registrations.sort_values(by=['RollNo'])
                for sti, strow in registrations.iterrows():
                    studentMarksRow = markDetails[markDetails['RegNo']==strow['RegNo']].iloc[0]
                    studentGradeRow = gradeDetails[gradeDetails['RegNo']==strow['RegNo']].iloc[0]
                    if(tl):
                        studentMarks = studentMarksRow['Marks'].split(',')[0].split('+') + studentMarksRow['Marks'].split(',')[1].split('+')
                    else:
                        studentMarks = studentMarksRow['Marks'].split('+')
                    studentMarks = [float(i) for i in studentMarks]
                    stDataRow = [sti + 1,strow['RegNo'],strow['RollNo'],strow['Name'],
                        month2num[strow['HeldInMonth']]+'-'+str(strow['HeldInYear']%100)]
                    stDataRowFormats = [formats['fc'],formats['fc'],formats['fc'],formats['fl'],formats['fc']]
                    for mIndex in range(len(mcols)):
                        stDataRow.append(studentMarks[mIndex])
                        stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentMarksRow['TotalMarks'])
                    stDataRowFormats.append(formats['fc'])

                    
                    if(studentGradeRow['Grade'] in passGrades):
                        stDataRow.append('P')
                    else:
                        stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    strowIndexZ = studentStartRowIndexZ + sti 
                    
                    for stdIndex in range(len(stDataRow)):
                        worksheet.write(strowIndexZ, stdIndex,stDataRow[stdIndex],stDataRowFormats[stdIndex])
                    
                    stIndex = stIndex + 1

        workbook.close()       

def generate_exam_finalized_template(ayear,asem,byear,bsem,dept,mode,regulation,flag, response):
    grades = {1:['P','F','I','X'],
          2: ['P','F','I','X'], 
          3:['P','F','I','X'], 
          4:['P','F','I','X']}
    alphas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
          'W', 'X', 'Y', 'Z']
    Years = ['I', 'II', 'III', 'IV']
    itor = {1:'I',2:'II',3:'III',4:'IV'}
    month2num={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','June':'06','July':'07',
            'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}

    rmode = 0
    rmodeStr = '-Exam'
    headerStr = ' Backlog Exam'
    notSubmitted = []
    height = 30
    if(BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Dept=dept,Mode=mode,Regulation=regulation,RMode=rmode).exists()):
        cursor = connection.cursor()
        cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Dept"={} and "Mode"=\'{}\' and "Regulation"={} and "RMode"={}'.format(ayear,asem,byear,bsem,dept,mode,regulation,rmode))
        registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Dept=dept,Mode=mode,Regulation=regulation,RMode=rmode)
        markDetails = pd.DataFrame(cursor.fetchall())
        if(flag==1):
            registrations = registrations.filter(~Q(Category='OPC')).filter(~Q(Category='OEC'))
            if((byear==4) or (byear==3)):
                registrations = registrations.filter(~Q(Category='MDC'))
            optSuffix = ''
        elif(flag==2):
            registrations = registrations.filter(Category='OPC')
            optSuffix = '-Open'
        elif(flag==3):
            if(byear==3 or byear==4):
                registrations = registrations.filter(Category='MDC')
                optSuffix = '-MDC'
            else:
                return 
        
        markDetails.columns = ['id','AYear','ASem','BYear','BSem','Regulation','Dept','RegEventId','Mode','SubId','SubCode','RMode','Distribution','DistributionNames','DistributionRatio','RegNo','Marks','TotalMarks','Registration_id']
        cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Dept"={} and "Mode"=\'{}\' and "Regulation"={} and "RMode"={}'.format(ayear,asem,byear,bsem,dept,mode,regulation,rmode))
        gradeDetails = pd.DataFrame(cursor.fetchall(),columns=['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','RMode','Grade'])
        cursor.execute('Select * from "BTGradeThresholdDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "Dept"={} and "Mode"=\'{}\' and "Regulation"={}'.format(ayear,asem,byear,bsem,dept,mode,regulation))
        gradeThresholdDetails = pd.DataFrame(cursor.fetchall(),columns =['id','AYear','ASem','BYear','BSem','Regulation','Mode','Dept','RegEventId','SubCode','G1','G2','G3','G4','G5','G6','G7','ET'] )
        if(registrations.count()!=0):
            print(registrations.count())
            print(str(dept)+'-'+str(byear))
            workbook = xlsxwriter.Workbook(response, {'in_memory':True})
            subjects = pd.DataFrame.from_records(registrations.values('sub_id','SubCode','SubName','Credits','Category','HeldInMonth','HeldInYear','Dept',)) 
            subjects = subjects.drop_duplicates(subset=['SubCode'],keep='first')
            subjects.sort_values(by=['SubCode'], inplace=True)
            subjectList = subjects['SubCode'].drop_duplicates().to_list()
            print(subjectList)
            markDetails = markDetails[markDetails['SubCode'].isin(subjectList)]
            gradeDetails = gradeDetails[gradeDetails['SubCode'].isin(subjectList)]
            gradeThresholdDetails = gradeThresholdDetails[gradeThresholdDetails['SubCode'].isin(subjectList)]
            N = 0
            noconsolidated = False
            for si, subject in subjects.iterrows():
                tl = False
                subjectObj = BTSubjects.objects.get(id=subject['sub_id'])
                subRegistrations = pd.DataFrame.from_records(registrations.filter(SubCode=subject['SubCode']).values())
                subMarkDetails = markDetails[markDetails['SubCode']==subject['SubCode']]
                subGradeDetails = gradeDetails[gradeDetails['SubCode']==subject['SubCode']]
                subGradeThresholdDetails = gradeThresholdDetails[gradeThresholdDetails['SubCode']==subject['SubCode']]
                print(subGradeThresholdDetails.shape)
                if(subGradeThresholdDetails.shape[0]==0 or subGradeDetails.shape[0]==0):
                    noconsolidated = True
                    notSubmitted.append(subject['SubCode'])
                    continue 

                if(subjectObj.OfferedBy!=dept):
                    continue
                
                subThresholds = {}
                for gIndex, g in enumerate(grades[regulation]):
                    if(g=='F'):
                        break
                    subThresholds[g] = subGradeThresholdDetails.iloc[0,10+gIndex]
                gradeStats = subGradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)
                for g in grades[regulation]:
                    if(not (g in gradeStats.columns)):
                        gradeStats.loc[:,g]=0
                subRegistrations.sort_values(by=['RollNo'],inplace=True)
                print(subject['SubCode'])
                worksheet = workbook.add_worksheet(subject['SubCode'])
                worksheet.protect()

                # Setting the title Rows
                formats = getFormats(workbook, False)
                colWidths = [8, 10,10,40,8,8,8,8,8,12,8,8]
                for colIndex in range(len(colWidths)):
                    worksheet.set_column(alphas[colIndex]+':'+alphas[colIndex], colWidths[colIndex], formats['f1'])  # S.NO
                worksheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                
                worksheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+' Semester AY-'+ str(ayear)+'-'+str(ayear+1) , formats['t2'])
                worksheet.merge_range('A4:M4', 'Subject Code: ' + str(subject['SubCode'])+ ' Subject Name: ' + 
                    subject['SubName'] + ' Credits: ' + str(subject['Credits']) + headerStr  , formats['t2'])
                startRowIndexZ = 5

                # Setting the Header Row
                worksheet.set_row(startRowIndexZ, height)
                headerCols = ['S.No','RegNo','RollNo','Name','MM/YY']
                for hIndex in range(len(headerCols)):
                    worksheet.write(startRowIndexZ, hIndex, headerCols[hIndex], formats['fb'])
                
                md = subjectObj.MarkDistribution
                print(md.Distribution)
                print(subjectObj.DistributionRatio)
                # For Exam Mode only End Exam Marks are to be used
                if(',' in md.Distribution):
                    print(md.Distribution)
                    tl = True
                    dists = md.Distribution.split(',')
                    mcols = [dists[0].split('+')[-1], dists[1].split('+')[-1]] 
                    distnames = md.DistributionNames.split(',')
                    mnames = [distnames[0].split('+')[-1],distnames[1].split('+')[-1]] 
                else:
                    tl = False
                    mcols = [md.Distribution.split('+')[-1]]
                    mnames = [md.DistributionNames.split('+')[-1]]
                numMarkCols = len(mcols)
                marksColSIndexZ = 5 
                totalColIndexZ = marksColSIndexZ + numMarkCols 
                mcolIndex = 0
                for mcol,mname in zip(mcols,mnames):
                    worksheet.write(startRowIndexZ, marksColSIndexZ+mcolIndex, mname+'('+mcol+')', formats['fbbc'])
                    mcolIndex+=1

                worksheet.write(startRowIndexZ, totalColIndexZ, 'Total(100)', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 1, 'Result', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 2, 'Grade', formats['fb'])
                studentStartRowIndexZ = 6
                stIndex = 0
                N_sub = subRegistrations.shape[0]
                if (N == 0):
                    df_p = subRegistrations
                    N = N_sub
                else:
                    df_p = pd.concat([df_p, subRegistrations]).drop_duplicates(subset='RegNo', keep='last')
                studentEndRowIndexZ = studentStartRowIndexZ + N_sub -1
                gtRowIndexZ =  studentEndRowIndexZ+4
                for gIndex, g in enumerate(grades[regulation]):
                    worksheet.write(gtRowIndexZ + gIndex, 0, g , formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex, 2, gradeStats.iloc[0][g],formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex,3, round(100*gradeStats.iloc[0][g]/N_sub,2))
                    if(gIndex<len(subThresholds)): #gIndex is before Index upto P grade
                        worksheet.write(gtRowIndexZ + gIndex, 1,subThresholds[g] , formats['fb'])
                
                totalRowIndexZ = gtRowIndexZ + len(grades[regulation])    
                # Write the header row for Grade Threshold Count Percentage Box
                for gIndex, gval in enumerate(['Grade','Threshold','Count','Percentage']):
                    worksheet.write(gtRowIndexZ-1, gIndex, gval, formats['fb'])
                
                # Total summing the number of students accounted in the grade threshold Counts
                worksheet.write(totalRowIndexZ, 0, 'Total', formats['fb'])
                worksheet.write(totalRowIndexZ, 2, N_sub, formats['fb'])
                # Stats to be printed under total marks column towards the bottom
                subRegistrations = subRegistrations.reset_index()
                subRegistrations = subRegistrations.sort_values(by=['RollNo'])
                for sti, strow in subRegistrations.iterrows():
                    studentMarksRow = subMarkDetails[subMarkDetails['RegNo']==strow['RegNo']].iloc[0]
                    studentGradeRow = subGradeDetails[subGradeDetails['RegNo']==strow['RegNo']].iloc[0]
                    if(tl):
                        studentMarks = [studentMarksRow['Marks'].split(',')[0].split('+')[-1] , studentMarksRow['Marks'].split(',')[1].split('+')[-1]]
                    else:
                        studentMarks = [studentMarksRow['Marks'].split('+')[-1]]
                    studentMarks = [float(i) for i in studentMarks]
                    stDataRow = [sti + 1,strow['RegNo'],strow['RollNo'],strow['Name'],
                        month2num[strow['HeldInMonth']] + '-' + str(strow['HeldInYear']%100)]
                    stDataRowFormats = [formats['fc'],formats['fc'],formats['fc'],formats['fl'],formats['fc']]
                    for mIndex in range(len(mcols)):
                        stDataRow.append(studentMarks[mIndex])
                        stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentMarksRow['TotalMarks'])
                    stDataRowFormats.append(formats['fc'])

                    
                    if(studentGradeRow['Grade'] == 'P'):
                        stDataRow.append('P')
                    else:
                        stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    strowIndexZ = studentStartRowIndexZ + sti 
                    
                    for stdIndex in range(len(stDataRow)):
                        worksheet.write(strowIndexZ, stdIndex,stDataRow[stdIndex],stDataRowFormats[stdIndex])
                    
                    stIndex = stIndex + 1
            if(not noconsolidated):
                df_p = pd.DataFrame(registrations.values('RegNo','RollNo','Name')).drop_duplicates(subset='RegNo', keep='last')
                N = df_p.shape[0]
                worksheet = workbook.add_worksheet('Consolidated')
                start = 6
                formats = getFormats(workbook, False)
                
                worksheet.set_column('A:A', 8, formats['f1'])  # S.NO
                worksheet.set_column('B:B', 10, formats['f1'])  # RegNo
                worksheet.set_column('C:C', 10, formats['f1'])  # RollNo
                worksheet.set_column('D:D', 40, formats['f1'])  # Na01`me
                
                worksheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                worksheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+ ' Semester AY-'+str(ayear)+'-'+str(ayear+1) + headerStr, formats['t2'])
                consolidatedHeader = ['S.No', 'RegNo', 'RollNo', 'Name'] +subjectList
                for sub in range(len(consolidatedHeader)):
                    worksheet.write(start - 1, sub, consolidatedHeader[sub], formats['fb'])
                
                stIndex = 0
                for stInd, student in df_p.iterrows():
                    studRow = [stIndex + 1,student['RegNo'],student['RollNo'],student['Name']]
                    studFormats = [formats['fc'],formats['fc'],formats['fc'],formats['fl']]
                    for stdi in range(len(studRow)):
                        worksheet.write(start + stIndex, stdi, studRow[stdi], studFormats[stdi])
                    studentGradeDetails = gradeDetails[gradeDetails['RegNo']==student['RegNo']]
                    for sub in range(len(subjectList)):
                        studentSubGradeDetails = studentGradeDetails[studentGradeDetails['SubCode']==subjectList[sub]]
                        studentGrade = ''
                        if(studentSubGradeDetails.shape[0]>0):
                            studentGrade = studentSubGradeDetails.iloc[0].Grade
                        worksheet.write(start + stIndex, sub+4,studentGrade,formats['fc'])
                    stIndex += 1
                endIndex = start + df_p.shape[0]
                for gIndex, g in enumerate(grades[regulation]):
                    worksheet.write(endIndex + 3+ gIndex, 3, g, formats['fbr'])
                
                for sub in range(4, 4 + len(subjectList)):
                    subGradeDetails = gradeDetails[gradeDetails['SubCode']==subjectList[sub-4]]
                    gradeStats = subGradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)

                    subEndIndex = start + subGradeDetails.shape[0]
                    for gIndex,g in enumerate(grades[regulation]):
                        if(not (g in gradeStats.columns)):
                            gradeStats.loc[:,g]=0
                        worksheet.write(endIndex + 3+ gIndex, sub, gradeStats.iloc[0][g], formats['fc'])
                    worksheet.write(endIndex + 3+ gIndex+1,sub,subGradeDetails.shape[0],formats['fc'])
            workbook.close()


def generate_backlog_subject_wise_grade_report(ayear,asem,byear, bsem, mode, regulation, subcode, depts, response):
    grades = {1:['P','F','I','X','W'],
          2: ['P','F','I','X','W'], 
          3:['P','F','I','X','W'], 
          4:['P','F','I','X','W']}
    Years = ['I', 'II', 'III', 'IV']
    alphas = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V',
            'W', 'X', 'Y', 'Z']
    itor = {1:'I',2:'II',3:'III',4:'IV'}
    month2num={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','June':'06','July':'07',
            'Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
    bchs = ['BTE', 'CHE', 'CE', 'CSE', 'EEE', 'ECE', 'ME', 'MME', 'Chemistry', 'Physics']
    
    height = 30
    rmode = 0
    headerStr = ' Backlog Exam'
    if(BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,RMode=rmode).exists()):
        registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,RMode=rmode)
        deptList = [depts]
        sheetNameList = [subcode]
        if(len(depts)>1):
            for dept in depts:
                deptList.append([dept])
                sheetNameList.append(subcode+'-'+bchs[dept-1])
        print(sheetNameList)
        regDF = pd.DataFrame.from_records(registrations.values())
        subIDs = regDF[['SubCode','Regulation','Dept','sub_id']].drop_duplicates(subset=['SubCode','Dept','Regulation'],keep='first')
        subIDsList = subIDs['sub_id'].drop_duplicates().to_list()
        subInfo = pd.DataFrame.from_records(BTSubjectInfo.objects.filter(SubId__in=subIDsList).values())
        print(subInfo.shape)
        subjects = pd.merge(subIDs[['sub_id']],subInfo,left_on='sub_id',right_on='SubId')
        
        workbook = xlsxwriter.Workbook(response, {'in_memory':True})
        print(subcode)
        print(depts)
        for di, deptItem in enumerate(deptList):
            worksheet = workbook.add_worksheet(sheetNameList[di])
            worksheet.protect()
            if(len(deptItem)>1):
                registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,RMode=rmode,Dept__in=deptItem)
                cursor = connection.cursor()
                cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "RMode"={} and "Regulation"={}'.format(ayear,asem,byear,bsem,subcode,mode,rmode,regulation))
                markDetails = pd.DataFrame(cursor.fetchall())
                cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "RMode"={} and "Regulation"={}'.format(ayear,asem,byear,bsem,subcode,mode, rmode, regulation))
                gradeDetails = pd.DataFrame(cursor.fetchall(),columns=['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','RMode','Grade'])
                cursor.execute('Select * from "BTGradeThresholdDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation))
                gradeThresholdDetails = pd.DataFrame(cursor.fetchall(),columns =['id','AYear','ASem','BYear','BSem','Regulation','Mode','Dept','RegEventId','SubCode','G1','G2','G3','G4','G5','G6','G7','ET'] )
                subject = subjects.iloc[0]
                markDetails.columns = ['id','AYear','ASem','BYear','BSem','Regulation','Dept','RegEventId','Mode','SubId','SubCode','RMode','Distribution','DistributionNames','DistributionRatio','RegNo','RollNo','Name','Marks','TotalMarks','Registration_id']
            else:
                registrations = BTRegistrationDetails.objects.filter(AYear=ayear,ASem=asem,BYear=byear,BSem=bsem,Mode=mode,Regulation=regulation,SubCode=subcode,Dept=deptItem[0],RMode=rmode)
                cursor = connection.cursor()
                cursor.execute('Select * from "BTStudentSubjectMarkDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "RMode"={} and "Dept"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,rmode,deptItem[0]))
                markDetails = pd.DataFrame(cursor.fetchall())
                markDetails.columns = ['id','AYear','ASem','BYear','BSem','Regulation','Dept','RegEventId','Mode','SubId','SubCode','RMode','Distribution','DistributionNames','DistributionRatio','RegNo','RollNo','Name','Marks','TotalMarks','Registration_id']
                cursor.execute('Select * from "BTStudentGradeDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={} and "RMode"={} and "Dept"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,rmode, deptItem[0]))
                gradeDetails = pd.DataFrame(cursor.fetchall(),columns=['id','RegNo','AYear','ASem','BYear','BSem','Mode','Dept','Regulation','SubCode','RMode','Grade'])
                cursor.execute('Select * from "BTGradeThresholdDetailsV" where "AYear" = {} and "ASem"= {} and "BYear"={} and "BSem"={} and "SubCode"=\'{}\' and "Mode"=\'{}\' and "Regulation"={}'.format(ayear,asem,byear,bsem,subcode,mode,regulation,deptItem[0]))
                gradeThresholdDetails = pd.DataFrame(cursor.fetchall(),columns =['id','AYear','ASem','BYear','BSem','Regulation','Mode','Dept','RegEventId','SubCode','G1','G2','G3','G4','G5','G6','G7','ET'] )
                subject = subjects[subjects['Dept']==deptItem[0]].iloc[0]
            if(registrations.count()!=0):
                print(registrations.count())
                registrations = pd.DataFrame.from_records(registrations.values())
                tl = False
                if(gradeThresholdDetails.shape[0]==0 or gradeDetails.shape[0]==0):
                    continue 
                subThresholds = {}
                for gIndex, g in enumerate(grades[regulation]):
                    if(g=='F'):
                        break
                    subThresholds[g] = gradeThresholdDetails.iloc[0]['ET']
                gradeStats = gradeDetails.pivot_table(values='RegNo',columns='Grade',aggfunc='count',fill_value=0)
                for g in grades[regulation]:
                    if(not (g in gradeStats.columns)):
                        gradeStats.loc[:,g]=0
                gradeStats = gradeStats[grades[regulation]]
                registrations.sort_values(by='RollNo')
                
                # Setting the title Rows
                formats = getFormats(workbook, True)
                colWidths = [8, 10,10,40,8,8,8,8,8,12,8,8]
                for colIndex in range(len(colWidths)):
                    worksheet.set_column(alphas[colIndex]+':'+alphas[colIndex], colWidths[colIndex], formats['f1'])  # S.NO
                worksheet.merge_range('A2:M2', 'NATIONAL INSTITUTE OF TECHNOLOGY ANDHRA PRADESH', formats['t1'])
                
                worksheet.merge_range('A3:M3', Years[byear - 1] + ' B.Tech. '+itor[asem]+' Semester AY-'+ str(ayear)+'-'+str(ayear+1) , formats['t2'])
                worksheet.merge_range('A4:M4', 'Subject Code: ' + sheetNameList[di]+ ' Subject Name: ' + 
                    subject['SubName'] + ' Credits: ' + str(subject['Credits']) + headerStr, formats['t2'])
                startRowIndexZ = 5

                # Setting the Header Row
                worksheet.set_row(startRowIndexZ, height)
                headerCols = ['S.No','RegNo','RollNo','Name','MM/YY']
                for hIndex in range(len(headerCols)):
                    worksheet.write(startRowIndexZ, hIndex, headerCols[hIndex], formats['fb'])
                subjectObj = BTSubjects.objects.get(id=subject['SubId'])
                md = subjectObj.MarkDistribution
                print(md.Distribution)
                print(subjectObj.DistributionRatio)
                if(',' in md.Distribution):
                    print(md.Distribution)
                    tl = True
                    dists = md.Distribution.split(',')
                    mcols = [dists[0].split('+')[-1], dists[1].split('+')[-1]] 
                    distnames = md.DistributionNames.split(',')
                    mnames = [distnames[0].split('+')[-1],distnames[1].split('+')[-1]] 
                else:
                    tl = False
                    mcols = [md.Distribution.split('+')[-1]]
                    mnames = [md.DistributionNames.split('+')[-1]]
                numMarkCols = len(mcols)
                marksColSIndexZ = 5 
                totalColIndexZ = marksColSIndexZ + numMarkCols 
                mcolIndex = 0
                for mcol,mname in zip(mcols,mnames):
                    worksheet.write(startRowIndexZ, marksColSIndexZ+mcolIndex, mname+'('+mcol+')', formats['fbbc'])
                    mcolIndex+=1
                worksheet.write(startRowIndexZ, totalColIndexZ, 'Total', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 1, 'Result', formats['fb'])
                worksheet.write(startRowIndexZ, totalColIndexZ + 2, 'Grade', formats['fb'])
                studentStartRowIndexZ = 6
                stIndex = 0
                N_sub = registrations.shape[0]
                studentEndRowIndexZ = studentStartRowIndexZ + N_sub -1
                gtRowIndexZ =  studentEndRowIndexZ+4
                for gIndex, g in enumerate(grades[regulation]):
                    worksheet.write(gtRowIndexZ + gIndex, 0, g , formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex, 2, gradeStats.iloc[0][g],formats['fb'])
                    worksheet.write(gtRowIndexZ + gIndex,3, round(100*gradeStats.iloc[0][g]/N_sub,2))
                    if(gIndex<len(subThresholds)): #gIndex is before Index upto P grade
                        worksheet.write(gtRowIndexZ + gIndex, 1,subThresholds[g] , formats['fb'])
                
                totalRowIndexZ = gtRowIndexZ + len(grades[regulation])    
                # Write the header row for Grade Threshold Count Percentage Box
                for gIndex, gval in enumerate(['Grade','Threshold','Count','Percentage']):
                    worksheet.write(gtRowIndexZ-1, gIndex, gval, formats['fb'])
                
                # Total summing the number of students accounted in the grade threshold Counts
                worksheet.write(totalRowIndexZ, 0, 'Total', formats['fb'])
                worksheet.write(totalRowIndexZ, 2, N_sub, formats['fb'])
                
                registrations = registrations.reset_index()
                registrations = registrations.sort_values(by=['RollNo'])
                print(registrations.shape)
                print(markDetails.shape)
                for sti, strow in registrations.iterrows():
                    if(markDetails[markDetails['RegNo']==strow['RegNo']].shape[0]==0):
                        print(strow['RegNo'])
                        print(strow['Dept'])
                        print(strow['SubCode'])
                    studentMarksRow = markDetails[markDetails['RegNo']==strow['RegNo']].iloc[0]
                    studentGradeRow = gradeDetails[gradeDetails['RegNo']==strow['RegNo']].iloc[0]
                    if(tl):
                        studentMarks = [studentMarksRow['Marks'].split(',')[0].split('+')[-1] , studentMarksRow['Marks'].split(',')[1].split('+')[-1]]
                    else:
                        studentMarks = [studentMarksRow['Marks'].split('+')[-1]]

                    studentMarks = [float(i) for i in studentMarks]
                    stDataRow = [sti + 1,strow['RegNo'],strow['RollNo'],strow['Name'],
                        month2num[strow['HeldInMonth']]+'-'+str(strow['HeldInYear']%100)]
                    stDataRowFormats = [formats['fc'],formats['fc'],formats['fc'],formats['fl'],formats['fc']]
                    for mIndex in range(len(mcols)):
                        stDataRow.append(studentMarks[mIndex])
                        stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentMarksRow['TotalMarks'])
                    stDataRowFormats.append(formats['fc'])

                    
                    if(studentGradeRow['Grade'] == 'P'):
                        stDataRow.append('P')
                    else:
                        stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    stDataRow.append(studentGradeRow['Grade'])
                    stDataRowFormats.append(formats['fc'])
                    strowIndexZ = studentStartRowIndexZ + sti 
                    
                    for stdIndex in range(len(stDataRow)):
                        worksheet.write(strowIndexZ, stdIndex,stDataRow[stdIndex],stDataRowFormats[stdIndex])
                    
                    stIndex = stIndex + 1
        workbook.close()       
