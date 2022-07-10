from asyncio.windows_events import NULL
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from co_ordinator.models import FacultyAssignment
from faculty.forms import AttendanceShoratgeStatusForm, AttendanceShoratgeUploadForm
from faculty.models import Attendance_Shortage, RegistrationStatus
from SupExamDBRegistrations.models import StudentInfo, RollLists, StudentRegistrations
from SupExamDBRegistrations.resources import FacultyInfoResource
from SupExamDB.views import is_Faculty
from django.contrib.auth.decorators import login_required, user_passes_test 
from django.contrib.auth import logout 
from django.db.models import F
from tablib import Dataset
from import_export.formats.base_formats import XLSX
from django.contrib.auth import get_user_model
from django.utils import timezone

from hod.models import Faculty_user

@login_required(login_url="/login/")
@user_passes_test(is_Faculty)
def attendance_shortage_upload(request):
    user = request.user
    faculty = Faculty_user.objects.filter(RevokeDate__isnull=True,User=user).first()
    subjects  = FacultyAssignment.objects.filter(Faculty=faculty,RegEventId__Status=1)
    if(request.method == 'POST'):
            form = AttendanceShoratgeUploadForm(subjects,request.POST)
        # if(form.is_valid()):
            sub = request.POST['Subjects'].split(':')[0]
            regEvent = request.POST['Subjects'].split(':')[1]
            section = request.POST['Subjects'].split(':')[2]
            
            file = request.FILES['file']
            
            data = bytes()
            for chunk in file.chunks():
                data+=chunk
            dataset = XLSX().create_dataset(data)

            roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section).values_list('student__RegNo', flat=True)
            errorRegNo = []
            for i in range(len(dataset)):
                regno = dataset[i][0]
                if regno not in roll_list:
                    errorRegNo.append(regno)
                    continue 
                student_registration = StudentRegistrations.objects.filter(RegNo=regno, RegEventId=regEvent, sub_id=sub)
                att_short = Attendance_Shortage.objects.filter(Registration=student_registration.first())
                if len(att_short) == 0 :
                    att_short = Attendance_Shortage(Registration=student_registration.first())
                    att_short.save()
                msg = 'Attendance Shortage Updated successfully.'
            return render(request, 'faculty/AttendanceShoratgeUpload.html', {'form':form, 'error':errorRegNo, 'msg':msg})
    else:
        
        form = AttendanceShoratgeUploadForm(subjects)
        return render(request, 'SupExamDBRegistrations/AttendanceShoratgeUpload.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(is_Faculty)
def attendance_shortage_status(request):
    user = request.user
    faculty = Faculty_user.objects.filter(RevokeDate__isnull=True,User=user).first()
    subjects  = FacultyAssignment.objects.filter(Faculty=faculty,RegEventId__Status=1)
    if(request.method == 'POST'):
        form = AttendanceShoratgeStatusForm(subjects,request.POST)
        sub = request.POST['Subjects'].split(':')[0]
        regEvent = request.POST['Subjects'].split(':')[1]
        section = request.POST['Subjects'].split(':')[2]
        roll_list = RollLists.objects.filter(RegEventId_id=regEvent, Section=section)
        att_short = Attendance_Shortage.objects.filter(Registration__RegEventId=regEvent, Registration__sub_id=sub, Registration__RegNo__in=roll_list.values_list('Student__RegNo', flat=True))
        return render(request, 'faculty/AttendanceShoratgeStatus.html',{'form':form ,'att_short':att_short})

    else:
        form = AttendanceShoratgeStatusForm(subjects)
    return render(request, 'faculty/AttendanceShoratgeStatus.html',{'form':form})


@login_required(login_url="/login/")
@user_passes_test(is_Faculty)
def attendance_shortage_delete(request,pk):
    att_short = Attendance_Shortage.objects.filter(id =pk)
    if len(att_short) != 0:
        att_short.delete()
    return render(request, 'faculty/AttendanceDeleteSuccess.html')
