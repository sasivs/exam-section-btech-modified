# from asyncio.windows_events import NULL
# from django.http import HttpResponseRedirect, HttpResponse
# from django.shortcuts import redirect, render
# from django.urls import reverse
# from SupExamDBRegistrations.forms import AttendanceShoratgeStatusForm, AttendanceShoratgeUploadForm,FacultyUserDeletionForm,FacultyAssignmentForm,FacultyDeletionForm,FacultyInfoUpdateForm,BacklogRegistrationForm, RegistrationsEventForm,FacultyUploadForm, \
#     SubjectsUploadForm, StudentRegistrationUpdateForm, SubjectDeletionForm, SubjectFinalizeEventForm, FacultyAssignmentStatusForm
# from SupExamDBRegistrations.models import Attendance_Shortage, Faculty_Coordinator, Faculty_user, FacultyInfo, RegistrationStatus, Regulation, StudentBacklogs, StudentInfo, StudentRegistrations, Subjects, Subjects_Staging,\
#     RollLists
# from SupExamDBRegistrations.resources import FacultyInfoResource
# from .home import is_Superintendent
# from django.contrib.auth.decorators import login_required, user_passes_test 
# from django.contrib.auth import logout 
# from django.db.models import F
# from tablib import Dataset
# from import_export.formats.base_formats import XLSX
# from django.contrib.auth import get_user_model
# from django.utils import timezone

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def attendance_shortage_upload(request):
#     if(request.method == 'POST'):
#             form = AttendanceShoratgeUploadForm(request.POST)
#         # if(form.is_valid()):
#             regId = request.POST['RegEvent']
            
#             file = request.FILES['file']
            
#             data = bytes()
#             for chunk in file.chunks():
#                 data+=chunk
#             dataset = XLSX().create_dataset(data)
#             for i in range(len(dataset)):
#                 regno = dataset[i][0]
#                 student = StudentInfo.objects.get(RegNo =regno)
#                 att_short = Attendance_Shortage.objects.filter(Student=student,RegEventId__id=regId)
#                 if len(att_short) == 0 :
#                     att_short = Attendance_Shortage(Student=student,RegEventId_id=regId)
#                     att_short.save()
#             return render(request, 'SupExamDBRegistrations/AttendanceShoratgeUploadSuccess.html')
            
#         # else:
#         #     print(form.errors)
#         #     for row in form.fields.values(): print(row)
#     else:
#         form = AttendanceShoratgeUploadForm()
#         return render(request, 'SupExamDBRegistrations/AttendanceShoratgeUpload.html',{'form':form})


# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def attendance_shortage_status(request):
#     if(request.method == 'POST'):
#             form = AttendanceShoratgeStatusForm(request.POST)

#             regId = request.POST['RegEvent']
#             request.session['regId'] = regId
            
#             att_short = Attendance_Shortage.objects.filter(RegEventId__id=regId)
#             return render(request, 'SupExamDBRegistrations/AttendanceShoratgeStatus.html',{'form':form ,'att_short':att_short})

            

#     else:
#         form = AttendanceShoratgeStatusForm()
#         return render(request, 'SupExamDBRegistrations/AttendanceShoratgeStatus.html',{'form':form})




        

# @login_required(login_url="/login/")
# @user_passes_test(is_Superintendent)
# def attendance_shortage_delete(request,pk):
#     regID = request.session.get('regId')
#     att_short = Attendance_Shortage.objects.filter(RegEventId__id=regID,Student__id =pk)
#     if len(att_short) != 0:
#         att_short.delete()
