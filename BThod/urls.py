from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from BThod.views import faculty_user_assignment, grades_finalize, marks_finalize, gpa


urlpatterns =[  

    path('BTGradesFinalize', grades_finalize.grades_finalize, name='BTGradesFinalize'),
    path('BTMarksFinalize', marks_finalize.marks_finalize, name='BTMarksFinalize'),

    path('BTCGPA', gpa.gpa_staging, name='CGPA'),

    path('BTFacultyUserAssignment', faculty_user_assignment.faculty_user, name = 'BTFacultyUserAssignment'),
    path('BTFacultyUserDetail/<int:pk>', faculty_user_assignment.faculty_user_detail, name='BTFacultyUserDetail'),
    path('BTFacultyUserRevoke/<int:pk>', faculty_user_assignment.faculty_user_revoke, name='BTFacultyUserRevoke'),

    path('BTFacultyCoordinatorAssignment', faculty_user_assignment.faculty_Coordinator, name = 'BTFacultyCoordinatorAssignment'),
    path('BTCoordinatorAssignmentStatus', faculty_user_assignment.faculty_Coordinator_Status, name = 'BTCoordinatorAssignmentStatus'),
    # path('BTFacultyCoordinatorDetail/<int:pk>', faculty_user_assignment.faculty_Coordinator_detail, name='BTFacultyCoordinatorDetail'),
    # path('BTFacultyCoordinatorRevoke/<int:pk>', faculty_user_assignment.faculty_Coordinator_revoke, name='BTFacultyCoordinatorRevoke'),
    

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
