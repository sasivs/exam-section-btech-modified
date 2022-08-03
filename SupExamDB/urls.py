from django.urls import path,include

from . import views
import Registrations

urlpatterns = [
    # path('sindex',views.sup_home, name='sindex'),
    # path("logout", views.logout_request, name="logout_request"),
    # path('home', views.sup_home, name='home'),
    path('SupBTPrinting', views.btech_printing_home, name='SupBTPrinting'),
    path('SupBTPrintingDeptWise', views.btech_printing_deptwise, name='SupBTPrintingDeptWise'),
    path('SupBTPrintingStudentWise', views.btech_printing_studentwise, name='SupBTPrintingStudentWise'),
    path('SupBTPrintingConsolidated', views.btech_printing_consolidated, name='SupBTPrintingConsolidated'),
    path('SupMTechPrinting', views.mtech_printing, name='SupMTechPrinting'),
    path('SupPhDPrinting', views.phd_printing, name='SupPhDPrinting'),
    #path('SupBTGradeProcessing', views.btech_makeup_summary_info, name ='SupBTGradeProcessing'),
    # path('FacultyInfo', views.ca_import,name='FacultyInfo'),
    # path('FacultyInfoUploadErrorHandler', views.ca_fi_upload_error_handler, name='FacultyInfoUploadErrorHandler'),
]