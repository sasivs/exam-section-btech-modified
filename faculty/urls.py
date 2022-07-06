from unicodedata import name
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

from faculty.views import attendance_shortage
from SupExamDB import views as supviews

urlpatterns =[
    path('AttendanceShoratgeUpload',attendance_shortage.attendance_shortage_upload,name='AttendanceShoratgeUpload'),
    path('AttendanceShoratgeStatus',attendance_shortage.attendance_shortage_status,name='AttendanceShoratgeStatus'),
    path('AttendanceShoratgeDelete/<int:pk>',attendance_shortage.attendance_shortage_delete,name='AttendanceShoratgeDelete'),

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
