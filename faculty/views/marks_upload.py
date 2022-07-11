from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse 
from superintendent.user_access_test import marks_upload_access
from django.shortcuts import render
from import_export.formats.base_formats import XLSX
from superintendent.models import RegistrationStatus
from ExamStaffDB.models import StudentInfo
from co_ordinator.models import RollLists, Subjects, StudentRegistrations
from hod.models import Faculty_user
from co_ordinator.models import FacultyAssignment
from faculty.models import Marks_Staging
from faculty.forms import MarksUploadForm, MarksStatusForm, MarksUpdateForm


@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_upload(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty, RevokeDate__isnull=True)
    if request.method == 'POST':
        form = MarksUploadForm(subjects, request.FILES, request.POST)
        if form.is_valid():
            if request.POST.get('submit'):
                subject = form.cleaned_data.get('subject').split(':')[0]
                regEvent = form.cleaned_data.get('subject').split(':')[1]
                section = form.cleaned_data.get('subject').split(':')[2]
                exam_outer_index = form.cleaned_data.get('exam-type').split(',')[0]
                exam_inner_index = form.cleaned_data.get('exam-type').split(',')[1]
                file = form.cleaned_data.get('file')
                roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section)
                marks_objects = Marks_Staging.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=subject, \
                    Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True))
                mark_distribution = Subjects.objects.get(id=subject).MarkDistribution
                mark_dis_limit = mark_distribution.get_mark_limit(exam_outer_index, exam_inner_index)
                data = bytes()
                for chunk in file.chunks():
                    data += chunk
                dataset = XLSX().create_dataset(data)
                sheet_col_index = mark_distribution.get_excel_column_index(exam_outer_index, exam_inner_index)
                invalidRegNo = []
                invalidMarks = []
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
                msg = 'Marks Upload for the selected exam has been done.'
                return render(request, 'faculty/MarksUpload.html', {'form':form, 'invalidRegNo':invalidRegNo, \
                    'invalidMarks':invalidMarks, 'msg':msg})
    else:
        form = MarksUploadForm(subjects=subjects)
    return render(request, 'faculty/MarksUpload.html', {'form':form}) 


@login_required(login_url="/login/")
@user_passes_test(marks_upload_access)
def marks_upload_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty, RevokeDate__isnull=True)
    if request.method == 'POST':
        form = MarksStatusForm(request.POST, subjects)
        if form.is_valid():
            subject = form.cleaned_data.get('subject').split(':')[0]
            regEvent = form.cleaned_data.get('subject').split(':')[1]
            section = form.cleaned_data.get('subject').split(':')[2]
            roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section)
            marks_objects = Marks_Staging.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=subject, \
                Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True))
            return render(request, 'faculty/MarksUploadStatus.html', {'form':form, 'marks':marks_objects})
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
            exam_outer_index = form.cleaned_data.get('exam-type').split(',')[0]
            exam_inner_index = form.cleaned_data.get('exam-type').split(',')[1]
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
def download_sample_excel_sheet(request):

    '''
    Using MarkStatusForm, as the required fields are same in this case and for marks status view. 
    '''

    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    faculty = None
    if 'Faculty' in groups:
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
    subjects = FacultyAssignment.objects.filter(Faculty=faculty, RevokeDate__isnull=True)
    if request.method == 'POST':
        form = MarksStatusForm(request.POST, subjects)
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