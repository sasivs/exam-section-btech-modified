from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from ExamStaffDB.views import FacultyInfo
from hod.views import faculty_user_assignment, grades_finalize


urlpatterns =[  

    path('GradesFinalize', grades_finalize.grades_finalize, name='GradesFinalize'),


    path('FacultyUserAssignment', faculty_user_assignment.faculty_user, name = 'FacultyUserAssignment'),
    path('FacultyUserDetail/<int:pk>', faculty_user_assignment.faculty_user_detail, name='FacultyUserDetail'),
    path('FacultyUserRevoke/<int:pk>', faculty_user_assignment.faculty_user_revoke, name='FacultyUserRevoke'),

    path('FacultyCoordinatorAssignment', faculty_user_assignment.faculty_Coordinator, name = 'FacultyCoordinatorAssignment'),
    # path('FacultyCoordinatorDetail/<int:pk>', faculty_user_assignment.faculty_Coordinator_detail, name='FacultyCoordinatorDetail'),
    # path('FacultyCoordinatorRevoke/<int:pk>', faculty_user_assignment.faculty_Coordinator_revoke, name='FacultyCoordinatorRevoke'),
    

]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
