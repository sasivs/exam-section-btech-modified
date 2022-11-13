from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse 
from BTsuperintendent.user_access_test import marks_upload_access, marks_status_access
from django.shortcuts import render
from import_export.formats.base_formats import XLSX
from ADAUGDB.models import BTRegistrationStatus
from BTsuperintendent.models import BTHOD, BTCycleCoordinator
from BTExamStaffDB.models import BTStudentInfo
from BTco_ordinator.models import BTRollLists, BTSubjects, BTStudentRegistrations
from BThod.models import BTFaculty_user, BTCoordinator
from BTco_ordinator.models import BTFacultyAssignment
from BTfaculty.models import BTMarks, BTMarks_Staging
from BTfaculty.forms import MarksUploadForm, MarksStatusForm, MarksUpdateForm
from django.db import transaction


@transaction.atomic
@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, MarksStatus=1, RegEventId__Status=1, RegEventId__MarksStatus=1)
    if request.method == 'POST':
        form = MarksUploadForm(subjects, request.POST, request.FILES)
        if form.is_valid():
            if request.POST.get('submit-form'):
                subject = form.cleaned_data.get('subject').split(':')[0]
                regEvent = form.cleaned_data.get('subject').split(':')[1]
                section = form.cleaned_data.get('subject').split(':')[2]
                marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId_id=regEvent, Registration__sub_id_id=subject, \
                    Registration__student__Section=section)
                mark_distribution = BTSubjects.objects.get(id=subject).course.MarkDistribution
                file = form.cleaned_data.get('file')
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                invalidRegNo = []
                invalidMarks = []
                if form.cleaned_data.get('exam-type') != 'all':
                    exam_outer_index = int(form.cleaned_data.get('exam-type').split(',')[0])
                    exam_inner_index = int(form.cleaned_data.get('exam-type').split(',')[1])
                    mark_dis_limit = mark_distribution.get_marks_limit(exam_outer_index, exam_inner_index)
                    sheet_col_index = mark_distribution.get_excel_column_index(exam_outer_index, exam_inner_index)
                    for row in dataset:
                        required_obj = marks_objects.filter(Registration__student__student__RegNo=row[0])
                        if not required_obj:
                            invalidRegNo.append(row)
                            continue
                        if mark_dis_limit < int(row[sheet_col_index]):
                            invalidMarks.append(row)
                            continue
                        required_obj = required_obj.first()
                        marks_string = required_obj.Marks.split(',')
                        marks = [mark.split('+') for mark in marks_string]
                        marks[exam_outer_index][exam_inner_index] = str(row[sheet_col_index])
                        marks = ['+'.join(mark) for mark in marks]
                        marks_string = ','.join(marks)
                        required_obj.Marks = marks_string
                        required_obj.TotalMarks = required_obj.get_total_marks()
                        required_obj.save()
                else:
                    marks_dis_list = mark_distribution.Distribution.split(',')
                    marks_dis_list = [dis.split('+') for dis in marks_dis_list]
                    for row in dataset:
                        required_obj = marks_objects.filter(Registration__student__student__RegNo=row[0])
                        if not required_obj:
                            invalidRegNo.append(row)
                            continue
                        required_obj = required_obj.first()
                        marks_string = required_obj.Marks.split(',')
                        marks = [mark.split('+') for mark in marks_string]
                        for outer in range(len(marks_dis_list)):
                            for inner in range(len(marks_dis_list[outer])):
                                mark_dis_limit = int(marks_dis_list[outer][inner])
                                sheet_col_index = mark_distribution.get_excel_column_index(outer, inner)
                                if mark_dis_limit < int(row[sheet_col_index]):
                                    invalidMarks.append(row)
                                    continue
                                marks[outer][inner] = str(row[sheet_col_index])
                        marks = ['+'.join(mark) for mark in marks]
                        marks_string = ','.join(marks)
                        required_obj.Marks = marks_string
                        required_obj.TotalMarks = required_obj.get_total_marks()
                        required_obj.save()

                msg = 'Marks Upload for the selected exam has been done.'
                return render(request, 'BTfaculty/MarksUpload.html', {'form':form, 'invalidRegNo':invalidRegNo, \
                    'invalidMarks':invalidMarks, 'msg':msg})
    else:
        form = MarksUploadForm(subjects=subjects)
    return render(request, 'BTfaculty/MarksUpload.html', {'form':form}) 


@login_required(login_url="/login/")
@user_passes_test(marks_status_access)
def marks_upload_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    subjects = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    elif 'Superintendent' in groups or 'Associate-Dean' in groups:
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Status=1)
    elif 'Co-ordinator' in groups:
        co_ordinator = BTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1)
    elif 'HOD' in groups:
        hod = BTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = BTCycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = BTFacultyAssignment.objects.filter(RegEventId__Dept=cycle_cord.Cycle, RegEventId__BYear=1, RegEventId__Status=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            subject_obj = BTSubjects.objects.get(id=subject)
            distribution = subject_obj.course.MarkDistribution.Distribution
            distributionNames =subject_obj.course.MarkDistribution.DistributionNames
            distribution =  distribution.split(',')
            distributionNames = distributionNames.split(',')
            distributionNames = [name.split('+') for name in distributionNames] 
            names_list = []
            for name in  distributionNames:
                names_list.extend(name)

            # roll_list = BTRollLists.objects.filter(RegEventId_id=regEvent, Section=section)
            marks_objects = BTMarks_Staging.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=subject, \
                Registration__student__Section=section).order_by('Registration__student__student__RegNo')
            fac_assign_obj = subjects.filter(Subject_id=subject, RegEventId_id=regEvent, Section=section).first()
            for rindex, mark in enumerate(marks_objects):
                mark.s_no = rindex+1
                # student_obj = BTStudentInfo.objects.filter(RegNo=mark.Registration.RegNo).first()
                # mark.student = student_obj
                mark.Marks_list = mark.get_marks_list() 
                mark.Status = fac_assign_obj.MarksStatus
            return render(request, 'BTfaculty/MarksUploadStatus.html', {'form':form, 'marks':marks_objects,'names':names_list})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'BTfaculty/MarksUploadStatus.html', {'form':form})
    
@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_update(request, pk):
    mark_obj = BTMarks_Staging.objects.get(id=pk)
    if request.method == 'POST':
        form = MarksUpdateForm(mark_obj, request.POST)
        if form.is_valid():
            exam_outer_index = int(form.cleaned_data.get('exam-type').split(',')[0])
            exam_inner_index = int(form.cleaned_data.get('exam-type').split(',')[1])
            marks_field = form.cleaned_data.get('mark')
            marks_string = mark_obj.Marks.split(',')
            marks = [mark.split('+') for mark in marks_string]
            marks[exam_outer_index][exam_inner_index] = str(marks_field)
            marks = ['+'.join(mark) for mark in marks]
            marks_string = ','.join(marks)
            mark_obj.Marks = marks_string
            mark_obj.TotalMarks = mark_obj.get_total_marks()
            mark_obj.save()
            msg = 'Marks updated successfully.'
            return render(request, 'BTfaculty/MarksUpdate.html', {'form':form, 'mark':mark_obj, 'msg':msg})
    else:
        form = MarksUpdateForm(mark=mark_obj)
    return render(request, 'BTfaculty/MarksUpdate.html', {'form':form, 'mark':mark_obj})


@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_hod_submission(request):
    
    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, MarksStatus=1, RegEventId__Status=1, RegEventId__MarksStatus=1)
    msg = ''
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            fac_assign_obj = subjects.filter(Subject_id=subject, RegEventId_id=regEvent, Section=section).first()
            fac_assign_obj.MarksStatus = 0
            fac_assign_obj.save()
            msg = 'Marks have been submitted to HOD successfully.'
    else:
        form = MarksStatusForm(subjects)
    return render(request, 'BTfaculty/MarksFinalize.html', {'form':form, 'msg':msg})

@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def download_sample_excel_sheet(request):

    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = BTFacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1, RegEventId__MarksStatus=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            # roll_list = BTRollLists.objects.filter(RegEventId_id=regEvent, Section=section)
            subject = BTSubjects.objects.get(id=subject)
            regEvent = BTRegistrationStatus.objects.get(id=regEvent)
            student_registrations = BTStudentRegistrations.objects.filter(RegEventId_id=regEvent.id, sub_id_id=subject.id, \
                student__Section=section)
            students = BTStudentInfo.objects.filter(RegNo__in=student_registrations.values_list('student__student__RegNo', flat=True))
            
            from BTfaculty.utils import SampleMarksUploadExcelSheetGenerator
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
            response['Content-Disposition'] = 'attachment; filename={subcode}({regevent}).xlsx'.format(regevent=regEvent.__str__(), subcode=subject.course.SubCode)
            BookGenerator = SampleMarksUploadExcelSheetGenerator(students, regEvent, subject)
            workbook = BookGenerator.generate_workbook()
            workbook.save(response)
            return response
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'BTfaculty/MarksUploadStatus.html', {'form':form})

def add_marks(file):
    import pandas as pd
    file = pd.read_excel(file)
    invalid_rows=[]
    for rIndex, row in file.iterrows():
        print(row)
        regEvent = BTRegistrationStatus.objects.filter(AYear=row[0], ASem=row[1], BYear=row[2], BSem=row[3], Dept=row[4], Regulation=row[5], Mode=row[6]).first()
        registration = BTStudentRegistrations.objects.filter(student__student__RegNo=row[9], RegEventId_id=regEvent.id, sub_id__SubCode=row[7]).first()
        marks_row = BTMarks_Staging.objects.filter(Registration_id=registration.id).first()
        if not marks_row:
            subject = BTSubjects.objects.get(id=registration.sub_id.id)
            mark_distribution = subject.MarkDistribution
            BTMarks_Staging.objects.create(Registration=registration, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
            BTMarks.objects.create(Registration=registration, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
            marks_row = BTMarks_Staging.objects.filter(Registration_id=registration.id).first()
        mark_dis = registration.sub_id.MarkDistribution
        dis_names = mark_dis.DistributionNames.split(',')
        distributions = [dis.split('+') for dis in dis_names]
        marks_dis_list = mark_dis.Distribution.split(',')
        marks_dis_list = [dis.split('+') for dis in marks_dis_list]
        marks_string = marks_row.Marks.split(',')
        marks = [mark.split('+') for mark in marks_string]
        mark_index = 10
        for outer in range(len(distributions)):
            for inner in range(len(distributions[outer])):
                mark_dis_limit = int(marks_dis_list[outer][inner])
                if mark_dis_limit < int(row[mark_index]):
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