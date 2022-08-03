from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from ExamStaffDB.views import StudInfo, IX_student, mandatory_credits, FacultyInfo

urlpatterns = [

    path('BTStudentInfoFileUpload',StudInfo.StudInfoFileUpload, name = 'BTStudentInfoFileUpload'),
    path('BTDownloadSampleStudentInfoSheet', StudInfo.download_sample_studentinfo_sheet, name='BTDownloadSampleStudentInfoSheet'),

    path('BTStudentInfoUploadErrorHandler', StudInfo.student_info_error_handler, name = 'BTStudentInfoUploadErrorHandler'),
    path('BTUpdateRollNumber', StudInfo.update_rollno, name='BTUpdateRollNumber'),

    path('BTMandatoryCredits',mandatory_credits.mandatory_credits_upload, name='BTMandatoryCredits'),

    path('BTIXGradeStudentsAdd', IX_student.ix_student_assignment, name='BTIXGradeStudentsAdd'),
    path('BTIXGradeStudentsStatus', IX_student.ix_student_status, name='BTIXGradeStudentsStatus'),


    path('BTFacultyInfoUpload', FacultyInfo.faculty_upload, name = 'BTFacultyInfoUpload'),
    path('BTFacultyInfoUploadErrorHandler', FacultyInfo.FacultyInfo_upload_error_handler, name = 'BTFacultyInfoUploadErrorHandler'),
    path('BTFacultyInfoStatus', FacultyInfo.FacultyInfo_upload_status, name = 'BTFacultyInfoStatus'),
    path('BTFacultyInfoDeletion', FacultyInfo.Faculty_delete, name = 'BTFacultyInfoDeletion'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)