from django.contrib.auth.decorators import login_required, user_passes_test 
from django.shortcuts import render
from django.http import HttpResponse
from MTfaculty.forms import AttendanceShoratgeStatusForm, AttendanceShoratgeUploadForm
from MTco_ordinator.models import MTFacultyAssignment, MTRollLists, MTStudentRegistrations
from MTfaculty.models import MTAttendance_Shortage
from MTsuperintendent.models import MTHOD
from MThod.models import MTCoordinator 
from MTsuperintendent.user_access_test import is_Faculty, attendance_shortage_status_access, sample_regno_sheet_access
from import_export.formats.base_formats import XLSX
from MThod.models import MTFaculty_user

@login_required(login_url="/login/")
@user_passes_test(is_Faculty)
def attendance_shortage_upload(request):
    user = request.user
    faculty = MTFaculty_user.objects.filter(RevokeDate__isnull=True,User=user).first()
    subjects  = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty,RegEventId__Status=1)
    if(request.method == 'POST'):
            form = AttendanceShoratgeUploadForm(subjects, request.POST, request.FILES)
        # if(form.is_valid()):
            sub = request.POST['Subjects'].split(':')[0]
            regEvent = request.POST['Subjects'].split(':')[1]
            section = request.POST['Subjects'].split(':')[2]
            
            file = request.FILES['file']
            
            data = bytes()
            for chunk in file.chunks():
                data+=chunk
            dataset = XLSX().create_dataset(data)

            roll_list = MTRollLists.objects.filter(RegEventId_id=regEvent, Section=section).values_list('student__RegNo', flat=True)
            errorRegNo = []
            for i in range(len(dataset)):
                regno = dataset[i][0]
                if regno not in roll_list:
                    errorRegNo.append(regno)
                    continue 
                student_registration = MTStudentRegistrations.objects.filter(RegNo=regno, RegEventId=regEvent, sub_id=sub)
                att_short = MTAttendance_Shortage.objects.filter(Registration=student_registration.first())
                if len(att_short) == 0 :
                    att_short = MTAttendance_Shortage(Registration=student_registration.first())
                    att_short.save()
                msg = 'Attendance Shortage Updated successfully.'
            return render(request, 'faculty/AttendanceShortageUpload.html', {'form':form, 'error':errorRegNo, 'msg':msg})
    else:
        
        form = AttendanceShoratgeUploadForm(subjects)
        return render(request, 'faculty/AttendanceShortageUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(attendance_shortage_status_access)
def attendance_shortage_status(request):
    user = request.user
    groups = user.groups.all().values_list('name', flat=True)
    subjects  = None
    if 'Faculty' in groups:
        faculty = MTFaculty_user.objects.filter(RevokeDate__isnull=True,User=user).first()
        subjects  = MTFacultyAssignment.objects.filter(Faculty=faculty.Faculty,RegEventId__Status=1)
    elif 'Superintendent' in groups:
        subjects = MTFacultyAssignment.objects.filter(RegEventId__Status=1)
    elif 'HOD' in groups:
        hod = MTHOD.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(Subject__OfferedBy=hod.Dept, RegEventId__Status=1)
    elif 'Co-ordinator' in groups:
        coordinator = MTCoordinator.objects.filter(User=user, RevokeDate__isnull=True).first()
        subjects = MTFacultyAssignment.objects.filter(RegEventId__MYear=coordinator.MYear, Subject__OfferedBy=coordinator.Dept, RegEventId__Status=1)
    if(request.method == 'POST'):
        form = AttendanceShoratgeStatusForm(subjects,request.POST)
        sub = request.POST['Subjects'].split(':')[0]
        regEvent = request.POST['Subjects'].split(':')[1]
        roll_list = MTRollLists.objects.filter(RegEventId_id=regEvent)
        att_short = MTAttendance_Shortage.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=sub, Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True)).order_by('Registration__RegNo')
        msg = ''
        if request.POST.get('delete'):
            att_short.filter(id=request.POST.get('delete')).delete()
            roll_list = MTRollLists.objects.filter(RegEventId_id=regEvent)
            att_short = MTAttendance_Shortage.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=sub, Registration__RegNo__in=roll_list.values_list('student__RegNo', flat=True)).order_by('Registration__RegNo')
            msg = 'Attendance shortage record has been deleted successfully'
        return render(request, 'faculty/AttendanceShoratgeStatus.html',{'form':form ,'att_short':att_short, 'msg':msg})

    else:
        form = AttendanceShoratgeStatusForm(subjects)
    return render(request, 'faculty/AttendanceShoratgeStatus.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(sample_regno_sheet_access)
def download_sample_attendance_shortage_sheet(request):
    from MTco_ordinator.utils import RegNoTemplateBookGenerator
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',)
    response['Content-Disposition'] = 'attachment; filename=sample-{model}.xlsx'.format(model='ModelTemplate')
    BookGenerator = RegNoTemplateBookGenerator()
    workbook = BookGenerator.generate_workbook()
    workbook.save(response)
    return response
