from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MTExamStaffDB.views import StudentInfo, IX_student, FacultyInfo

urlpatterns = [

    path('MTStudentInfoFileUpload',StudentInfo.StudInfoFileUpload, name = 'MTStudentInfoFileUpload'),
    path('MTDownloadSampleStudentInfoSheet', StudentInfo.download_sample_studentinfo_sheet, name='MTDownloadSampleStudentInfoSheet'),
    path('MTStudentInfoUploadErrorHandler', StudentInfo.student_info_error_handler, name = 'MTStudentInfoUploadErrorHandler'),


    path('MTIXGradeStudentsAdd', IX_student.ix_student_assignment, name='MTIXGradeStudentsAdd'),
    path('MTIXGradeStudentsStatus', IX_student.ix_student_status, name='MTIXGradeStudentsStatus'),


    path('MTFacultyInfoUpload', FacultyInfo.faculty_upload, name = 'MTFacultyInfoUpload'),
    path('MTFacultyInfoUploadErrorHandler', FacultyInfo.FacultyInfo_upload_error_handler, name = 'MTFacultyInfoUploadErrorHandler'),
    path('MTFacultyInfoStatus', FacultyInfo.FacultyInfo_upload_status, name = 'MTFacultyInfoStatus'),
    path('MTFacultyInfoDeletion', FacultyInfo.Faculty_delete, name = 'MTFacultyInfoDeletion'),
    path('MTDownloadSampleFacultyInfoSheet', FacultyInfo.download_sample_facultyInfo_sheet, name='MTDownloadSampleFacultyInfoSheet'),


]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)