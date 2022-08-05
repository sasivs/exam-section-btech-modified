from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from BTfaculty.views import attendance_shortage, grades_threshold, courses, marks_upload, grades_generate

urlpatterns =[
    path('BTAttendanceShoratgeUpload',attendance_shortage.attendance_shortage_upload,name='BTAttendanceShoratgeUpload'),
    path('BTDownloadSampleAttendanceShortageSheet', attendance_shortage.download_sample_attendance_shortage_sheet, name='BTDownloadSampleAttendanceShortageSheet'),
    path('BTAttendanceShoratgeStatus',attendance_shortage.attendance_shortage_status,name='BTAttendanceShoratgeStatus'),
    path('BTGradesThreshold', grades_threshold.grades_threshold, name='BTGradesThreshold'),
    path('BTGradesThresholdAssign/<int:pk>', grades_threshold.grades_threshold_assign, name='BTGradesThresholdAssign'),
    path('BTGradesThresholdStatus', grades_threshold.grades_threshold_status, name='BTGradesThresholdStatus'),
    path('BTCoursesAssigned', courses.courses_assigned, name='BTCoursesAssigned'),
    path('BTMarksUpload', marks_upload.marks_upload, name='BTMarksUpload'),
    path('BTMarksUploadStatus', marks_upload.marks_upload_status, name='BTMarksUploadStatus'),
    path('BTMarksUpdate/<int:pk>', marks_upload.marks_update, name='BTMarksUpdate'),
    path('BTMarksHodSubmission', marks_upload.marks_hod_submission, name='BTMarksHodSubmission'),
    path('BTSampleMarksExcelSheetDownload', marks_upload.download_sample_excel_sheet, name='BTSampleMarksExcelSheetDownload'),
    path('BTGradesGenerate', grades_generate.grades_generate, name='BTGradesGenerate'),
    path('BTGradesStatus', grades_generate.grades_status, name='BTGradesStatus'),
    path('BTGradesHodSubmission', grades_generate.grades_hod_submission, name='BTGradesHodSubmission'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
