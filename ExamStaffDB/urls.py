from django.urls import path

from ExamStaffDB.views import StudInfo, IX_student

urlpatterns = [

    path('StudentInfoFileUpload',StudInfo.StudInfoFileUpload, name = 'StudentInfoFileUpload'),
    path('StudentInfoUploadErrorHandler', StudInfo.student_info_error_handler, name = 'StudentInfoUploadErrorHandler'),
    path('UpdateRollNumber', StudInfo.update_rollno, name='UpdateRollNumber'),

    path('IXGradeStudentsAdd', IX_student.ix_student_assignment, name='IXGradeStudentsAdd'),
    path('IXGradeStudentsStatus', IX_student.ix_student_status, name='IXGradeStudentsStatus'),

]
