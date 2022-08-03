from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse 
from superintendent.user_access_test import marks_upload_access, marks_status_access
from django.shortcuts import render
from import_export.formats.base_formats import XLSX
from superintendent.models import RegistrationStatus, HOD, CycleCoordinator
from ExamStaffDB.models import StudentInfo
from co_ordinator.models import RollLists, Subjects, StudentRegistrations
from hod.models import Faculty_user, Coordinator
from co_ordinator.models import FacultyAssignment
from faculty.models import Marks, Marks_Staging
from faculty.forms import MarksUploadForm, MarksStatusForm, MarksUpdateForm


@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, MarksStatus=1, RegEventId__Status=1, RegEventId__MarksStatus=1)
    if request.method == 'POST':
        form = MarksUploadForm(subjects, request.POST, request.FILES)
        if form.is_valid():
            if request.POST.get('submit-form'):
                subject = form.cleaned_data.get('subject').split(':')[0]
                regEvent = form.cleaned_data.get('subject').split(':')[1]
                section = form.cleaned_data.get('subject').split(':')[2]
                roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section)
                marks_objects = Marks_Staging.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=subject, \
                    Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True))
                mark_distribution = Subjects.objects.get(id=subject).MarkDistribution
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
                        required_obj = marks_objects.filter(Registration__RegNo=row[0])
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
                        required_obj = marks_objects.filter(Registration__RegNo=row[0])
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
                return render(request, 'faculty/MarksUpload.html', {'form':form, 'invalidRegNo':invalidRegNo, \
                    'invalidMarks':invalidMarks, 'msg':msg})
    else:
        form = MarksUploadForm(subjects=subjects)
    return render(request, 'faculty/MarksUpload.html', {'form':form}) 


@login_required(login_url="/login/")
@user_passes_test(marks_status_access)
def marks_upload_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    subjects = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1)
    elif 'Superintendent' in groups:
        subjects = FacultyAssignment.objects.filter(RegEventId__Status=1)
    elif 'Co-ordinator' in groups:
        co_ordinator = Coordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(Faculty__Dept=co_ordinator.Dept, RegEventId__Status=1)
    elif 'HOD' in groups:
        hod = HOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(Faculty__Dept=hod.Dept, RegEventId__Status=1)
    elif 'Cycle-Co-ordinator' in groups:
        cycle_cord = CycleCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = FacultyAssignment.objects.filter(RegEventId__Dept=cycle_cord.Cycle, RegEventId__BYear=1, RegEventId__Status=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            subject_obj = Subjects.objects.get(id=subject)
            distribution = subject_obj.MarkDistribution.Distribution
            distributionNames =subject_obj.MarkDistribution.DistributionNames
            distribution =  distribution.split(',')
            distributionNames = distributionNames.split(',')
            distributionNames = [name.split('+') for name in distributionNames] 
            names_list = []
            for name in  distributionNames:
                names_list.extend(name)

            roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section)
            marks_objects = Marks_Staging.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=subject, \
                Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True)).order_by('Registration__RegNo')
            fac_assign_obj = subjects.filter(Subject_id=subject, RegEventId_id=regEvent, Section=section).first()
            for mark in marks_objects:
                mark.Marks_list = mark.get_marks_list() 
                mark.Status = fac_assign_obj.MarksStatus
            return render(request, 'faculty/MarksUploadStatus.html', {'form':form, 'marks':marks_objects,'names':names_list})
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'faculty/MarksUploadStatus.html', {'form':form})
    
@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_update(request, pk):
    mark_obj = Marks_Staging.objects.get(id=pk)
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
            return render(request, 'faculty/MarksUpdate.html', {'form':form, 'mark':mark_obj, 'msg':msg})
    else:
        form = MarksUpdateForm(mark=mark_obj)
    return render(request, 'faculty/MarksUpdate.html', {'form':form, 'mark':mark_obj})


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
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, MarksStatus=1, RegEventId__Status=1, RegEventId__MarksStatus=1)
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
    return render(request, 'faculty/MarksFinalize.html', {'form':form, 'msg':msg})

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
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty.Faculty, RegEventId__Status=1, RegEventId__MarksStatus=1)
    if request.method == 'POST':
        form = MarksStatusForm(subjects, request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section)
            subject = Subjects.objects.get(id=subject)
            regEvent = RegistrationStatus.objects.get(id=regEvent)
            student_registrations = StudentRegistrations.objects.filter(RegEventId=regEvent.id, sub_id=subject.id, \
                RegNo__in=roll_list.values_list('student__RegNo', flat=True))
            students = StudentInfo.objects.filter(RegNo__in=student_registrations.values_list('RegNo', flat=True))
            
            from faculty.utils import SampleMarksUploadExcelSheetGenerator
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
            response['Content-Disposition'] = 'attachment; filename={subcode}({regevent}).xlsx'.format(regevent=regEvent.__str__(), subcode=subject.SubCode)
            BookGenerator = SampleMarksUploadExcelSheetGenerator(students, regEvent, subject)
            workbook = BookGenerator.generate_workbook()
            workbook.save(response)
            return response
    else:
        form = MarksStatusForm(subjects=subjects)
    return render(request, 'faculty/MarksUploadStatus.html', {'form':form})