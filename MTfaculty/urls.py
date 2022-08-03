from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MTfaculty.views import attendance_shortage, grades_threshold, courses, marks_upload, grades_generate

urlpatterns =[
    path('MTAttendanceShoratgeUpload',attendance_shortage.attendance_shortage_upload,name='MTAttendanceShoratgeUpload'),
    path('MTDownloadSampleAttendanceShortageSheet', attendance_shortage.download_sample_attendance_shortage_sheet, name='MTDownloadSampleAttendanceShortageSheet'),
    path('MTAttendanceShoratgeStatus',attendance_shortage.attendance_shortage_status,name='MTAttendanceShoratgeStatus'),
    path('MTGradesThreshold', grades_threshold.grades_threshold, name='MTGradesThreshold'),
    path('MTGradesThresholdAssign/<int:pk>', grades_threshold.grades_threshold_assign, name='MTGradesThresholdAssign'),
    path('MTGradesThresholdStatus', grades_threshold.grades_threshold_status, name='MTGradesThresholdStatus'),
    path('MTCoursesAssigned', courses.courses_assigned, name='MTCoursesAssigned'),
    path('MTMarksUpload', marks_upload.marks_upload, name='MTMarksUpload'),
    path('MTMarksUploadStatus', marks_upload.marks_upload_status, name='MTMarksUploadStatus'),
    path('MTMarksUpdate/<int:pk>', marks_upload.marks_update, name='MTMarksUpdate'),
    path('MTMarksHodSubmission', marks_upload.marks_hod_submission, name='MTMarksHodSubmission'),
    path('MTSampleMarksExcelSheetDownload', marks_upload.download_sample_excel_sheet, name='MTSampleMarksExcelSheetDownload'),
    path('MTGradesGenerate', grades_generate.grades_generate, name='MTGradesGenerate'),
    path('MTGradesStatus', grades_generate.grades_status, name='MTGradesStatus'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
