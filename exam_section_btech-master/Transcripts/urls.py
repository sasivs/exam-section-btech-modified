from django.urls import path

from . import views

urlpatterns = [
    path('BTechPrinting', views.btech_printing, name='BTech'),
    path('BTechPrintingDeptWise', views.btech_printing_deptwise, name='BTechDeptWise'),
    path('BTechPrintingDeptWisePaginated', views.btech_printing_deptwise_paginated, name='BTechDeptWisePaginated'),
    path('BTechPrintingDeptWiseStudentPages/<str:idtype>/<int:dept>/<int:event>', views.btech_printing_dept_wise_studentpage, name='BTechPrintingDeptWiseStudentPages'),
    path('BTechPrintingStudentGradePages/<int:regNo>', views.btech_printing_studentpages, name='BTechPrintingStudentGradePages'),
    path('BTechPrintingStudentWise', views.btech_printing_studentwise, name='BTechStudentWise'),
    path('BTechPrintingConsolidated', views.btech_printing_consolidated, name='BTechConsolidated'),
    path('BTechCMM',views.btech_cmm,name='BTechCMM'),
    path('BTechGetCMMData/<int:department>',views.btech_get_cmmdata_dept,name='BTechGetCMMDeptData'),
    path('BTechGetCMMGrades/<int:regNo>',views.btech_get_cmm_grades,name='BTechGetCMMGrades'),
    path('MTechPrinting', views.mtech_printing, name='MTech'),
    path('PhDPrinting', views.phd_printing, name='PhD'),
    path('BTechGetProgrammeData', views.get_programme_json, name = 'BTechGetProgrammeData'),
    path('BTechGetProgrammeData/<int:department>', views.get_programme_events_json, name = 'BTechGetProgrammeEventsData'),
    path('testview/<int:dept>', views.test_view_name, name='testname'),
    path('BTechGetProgrammeData/<int:department>/<int:event>', views.get_event_regNos, name = 'BTechGetEventRegNosData'),
    path('BTechGetStudentEvents/<int:regno>/',views.get_regno_events, name='BTechGetStudentEvents'),
    path('StudentRegNoGrades/<int:regno>/<int:ayasbybs>', views.get_student_regno_grades, name = 'StudentRegNoGrades'),
    path('StudentRollNoGrades/<int:rollno>/<int:ayasbybs>', views.get_student_rollno_grades, name = 'StudentRollNoGrades'),
    path('StudentCGPA/<str:option>/<int:regno>/<int:ayasbybs>', views.get_student_cgpa, name = 'StudentCGPA'),
    path('GetBTechIDs/<int:admissionYear>/<int:dept>', views.get_btech_ids, name='GetBTechIDs'),
    path('HeldIn/<int:ayasbybs>', views.get_heldin_info, name='HeldIn'),
    path('Test', views.test_view, name='Test'),
    path('', views.my_view, name='Index'),
]
