from django.urls import path

from . import views

urlpatterns = [
    path('SupBTPrinting', views.btech_printing_home, name='SupBTPrinting'),

    path('BTechPrinting', views.btech_printing, name='BTech'),

    path('BTechPrintingDeptWise', views.btech_printing_deptwise, name='BTechDeptWise'),
    path('MTechPrintingDeptWise', views.mtech_printing_deptwise, name='MTechDeptWise'),

    path('BTechPrintingDeptWisePaginated', views.btech_printing_deptwise_paginated, name='BTechDeptWisePaginated'),
    path('MTechPrintingDeptWisePaginated', views.mtech_printing_deptwise_paginated, name='MTechDeptWisePaginated'),

    path('BTechPrintingDeptWiseStudentPages/<str:idtype>/<int:dept>/<int:event>', views.btech_printing_dept_wise_studentpage, name='BTechPrintingDeptWiseStudentPages'),
    path('MTechPrintingDeptWiseStudentPages/<str:idtype>/<int:dept>/<int:event>', views.mtech_printing_dept_wise_studentpage, name='MTechPrintingDeptWiseStudentPages'),

    path('BTechPrintingStudentGradePages/<int:regNo>', views.btech_printing_studentpages, name='BTechPrintingStudentGradePages'),
    path('MTechPrintingStudentGradePages/<int:regNo>', views.mtech_printing_studentpages, name='MTechPrintingStudentGradePages'),

    path('BTechPrintingStudentWise', views.btech_printing_studentwise, name='BTechStudentWise'),
    path('MTechPrintingStudentWise', views.mtech_printing_studentwise, name='MTechStudentWise'),

    path('BTechPrintingConsolidated/<int:regno>', views.btech_printing_consolidated, name='BTechConsolidated'),
    path('MTechPrintingConsolidated/<int:regno>', views.mtech_printing_consolidated, name='MTechConsolidated'),

    path('BTechCMM',views.btech_cmm,name='BTechCMM'),

    path('BTechGetCMMData/<int:department>',views.btech_get_cmmdata_dept,name='BTechGetCMMDeptData'),
    path('MTechGetCMMData/<int:department>',views.mtech_get_cmmdata_dept,name='MTechGetCMMDeptData'),

    path('BTechGetCMMGrades/<int:regNo>',views.btech_get_cmm_grades,name='BTechGetCMMGrades'),


    path('MTechPrinting', views.mtech_printing, name='MTech'),
    path('PhDPrinting', views.phd_printing, name='PhD'),

    path('BTechGetProgrammeData', views.get_BT_programme_json, name = 'BTechGetProgrammeData'),
    path('MTechGetProgrammeData', views.get_MT_programme_json, name = 'MTechGetProgrammeData'),

    path('BTechGetProgrammeData/<int:department>', views.get_BT_programme_events_json, name = 'BTechGetProgrammeEventsData'),
    path('MTechGetProgrammeData/<int:department>', views.get_MT_programme_events_json, name = 'MTechGetProgrammeEventsData'),


    # path('testview/<int:dept>', views.test_view_name, name='testname'),


    path('BTechGetProgrammeData/<int:department>/<int:event>', views.get_BT_event_regNos, name = 'BTechGetEventRegNosData'),
    path('MTechGetProgrammeData/<int:department>/<int:event>', views.get_MT_event_regNos, name = 'MTechGetEventRegNosData'),

    path('BTechGetStudentEvents/<int:regno>/',views.get_BT_regno_events, name='BTechGetStudentEvents'),
    path('MTechGetStudentEvents/<int:regno>/',views.get_MT_regno_events, name='MTechGetStudentEvents'),

    
    # path('StudentRegNoGrades/<int:regno>/<int:ayasbybs>', views.get_student_regno_grades, name = 'StudentRegNoGrades'),
    # path('StudentRollNoGrades/<int:rollno>/<int:ayasbybs>', views.get_student_rollno_grades, name = 'StudentRollNoGrades'),


    path('GetBTechIDs/<int:admissionYear>/<int:dept>', views.get_btech_ids, name='GetBTechIDs'),
    path('GetMTechIDs/<int:admissionYear>/<int:dept>', views.get_mtech_ids, name='GetMTechIDs'),

    path('BTStudentCGPA/<str:option>/<int:regno>/<int:ayasbybs>', views.get_BT_student_cgpa, name = 'BTStudentCGPA'),
    path('MTStudentCGPA/<str:option>/<int:regno>/<int:ayasmyms>', views.get_MT_student_cgpa, name = 'MTStudentCGPA'),
    
    path('BTHeldIn/<int:ayasbybs>', views.get_BT_heldin_info, name='BTHeldIn'),
    path('MTHeldIn/<int:ayasmyms>', views.get_MT_heldin_info, name='MTHeldIn'),

    path('Test', views.test_view, name='Test'),
    path('', views.my_view, name='Index'),
]
