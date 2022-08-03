from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MThod.views import faculty_user_assignment, grades_finalize, marks_finalize, gpa


urlpatterns =[  

    path('MTGradesFinalize', grades_finalize.grades_finalize, name='MTGradesFinalize'),
    path('MTMarksFinalize', marks_finalize.marks_finalize, name='MTMarksFinalize'),

    path('MTCGPA', gpa.gpa_staging, name='MTCGPA'),


    path('MTFacultyUserAssignment', faculty_user_assignment.faculty_user, name = 'MTFacultyUserAssignment'),
    path('MTFacultyUserDetail/<int:pk>', faculty_user_assignment.faculty_user_detail, name='MTFacultyUserDetail'),
    path('MTFacultyUserRevoke/<int:pk>', faculty_user_assignment.faculty_user_revoke, name='MTFacultyUserRevoke'),

    path('MTFacultyCoordinatorAssignment', faculty_user_assignment.faculty_Coordinator, name = 'MTFacultyCoordinatorAssignment'),
    path('MTCoordinatorAssignmentStatus', faculty_user_assignment.faculty_Coordinator_Status, name = 'MTCoordinatorAssignmentStatus'),
    # path('FacultyCoordinatorDetail/<int:pk>', faculty_user_assignment.faculty_Coordinator_detail, name='FacultyCoordinatorDetail'),
    # path('FacultyCoordinatorRevoke/<int:pk>', faculty_user_assignment.faculty_Coordinator_revoke, name='FacultyCoordinatorRevoke'),
    

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
