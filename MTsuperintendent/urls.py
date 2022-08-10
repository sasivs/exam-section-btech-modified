from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from MTsuperintendent.views import Marks_Distribution, add_regulation, grade_points,\
    cancellations, hod_assignment,home, open_elective_registrations, heldin
    


urlpatterns = [
    path('MTsindex',home.sup_home, name='MTsindex'),
    path("logout", home.logout_request, name="logout_request"),
    path('MThome', home.sup_home, name='MThome'),
    path('MTSupBTPreRegistrationHome', home.pre_registrations_home, name="MTSupBTPreRegistrationHome"),
    path('MTSupBTRegistrationHome', home.registration_home, name = 'MTSupBTRegistrationHome'),
    path('MTSupBTRollListHome', home.rolllist_home, name='MTSupBTRollListHome'),
    path('MTSupBTSubjectHome', home.subject_home, name = 'MTSupBTSubjectHome'),
    path('MTSupBTGradesHome', home.grades_home, name="MTSupBTGradesHome"),
    path('MTSupBTFacultyHome', home.faculty_home, name='MTSupBTFacultyHome'),
    path('MTSupBTMarksHome', home.marks_home, name='MTSupBTMarksHome'),
    path('MTSupBTUserManagementHome', home.userassignment_home, name='MTSupBTUserManagementHome'),
    path('MTSupBTRegistrationStatusHome', home.mtech_registration_status_home, name = 'MTSupBTRegistrationStatusHome'),
    path('MTSupBTCancellationHome', home.cancellation_home, name='MTSupBTCancellationHome'),

    path('MTAddRegulation', add_regulation.addRegulation, name = 'MTAddRegulation'),

    # path('MTCreateRegistrationEvent', create_registration_event.create_registration_event, name='MTCreateRegistrationEvent'),

    # path('MTUpdateManageRegistrations', create_registration_event.update_manage_registrations,name='MTUpdateManageRegistrations'),

    path('MTOpenElectiveRegistrations',open_elective_registrations.open_elective_regs, name='MTOpenElectiveRegistrations'),


    path('MTGradePointsUpload', grade_points.grade_points_upload, name='MTGradePointsUpload'),
    path('MTGradePointsStatus', grade_points.grade_points_status, name='MTGradePointsStatus'),
    path('MTGradePointsUploadErrorHandler', grade_points.grade_points_upload_error_handler, name='MTGradePointsUploadErrorHandler'),


    path('MTHodAssignment', hod_assignment.hod_assignment, name='MTHodAssignment'),
    path('MTHodAssignmentStatus', hod_assignment.hod_assignment_status, name='MTHodAssignmentStatus'),

    path('MTAddMarkDistribution', Marks_Distribution.mark_distribution_add, name='MTAddMarkDistribution'),
    path('MTMarkDistributionStatus', Marks_Distribution.mark_distribution_status, name='MTMarkDistributionStatus'),
    path('MTMarksDistributionUpdate/<int:id>', Marks_Distribution.mark_distribution_update, name='MTMarksDistributionUpdate'),

    path('MTSupBTSeatCancellation',cancellations.seat_cancellation,name='MTSupBTSeatCancellation'),

    path('MTHeldIn', heldin.update_heldin, name='MTHeldIn'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)