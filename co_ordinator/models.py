from django.db import models
from SupExamDBRegistrations.models import RegistrationStatus, Subjects, FacultyInfo


# Create your models here.

class FacultyAssignment(models.Model):
    Subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
    Faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE, related_name='faculty_facultyInfo')
    Coordinator = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE, related_name='co_ordinator_facultyInfo')
    Section = models.CharField(max_length=2, default='NA')

    class Meta:
        db_table = 'FacultyAssignment'
        unique_together = (
            ('Subject', 'RegEventId', 'Coordinator'), 
            ('Subject', 'RegEventId', 'Faculty', 'Section')
        )
        managed = True