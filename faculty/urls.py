from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from faculty.views import attendance_shortage, grades_threshold, courses

urlpatterns =[
    path('AttendanceShoratgeUpload',attendance_shortage.attendance_shortage_upload,name='AttendanceShoratgeUpload'),
    path('AttendanceShoratgeStatus',attendance_shortage.attendance_shortage_status,name='AttendanceShoratgeStatus'),
    path('AttendanceShoratgeDelete/<int:pk>',attendance_shortage.attendance_shortage_delete,name='AttendanceShoratgeDelete'),
    path('GradesThreshold', grades_threshold.grades_threshold, name='GradesThreshold'),
    path('GradesThresholdAssign/<int:pk>', grades_threshold.grades_threshold_assign, name='GradesThresholdAssign'),
    path('CoursesAssigned', courses.courses_assigned, name='CoursesAssigned'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
