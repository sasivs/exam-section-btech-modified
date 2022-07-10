from enum import unique
from django.db import models
from SupExamDBRegistrations.models import RegistrationStatus, StudentRegistrations, Subjects, FacultyInfo, StudentInfo


# Create your models here.

class NotRegistered(models.Model):
    RegEventId= models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
    Student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    Registered = models.BooleanField()
    class Meta:
        db_table = 'NotRegistered'
        unique_together = (('RegEventId', 'student'))
        managed = False

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

class GradeChallenge(models.Model):
    Registration = models.ForeignKey(StudentRegistrations, on_delete=models.CASCADE)
    prev_marks = models.TextField()
    updated_marks = models.TextField()
    prev_grade = models.CharField(max_length=2)
    updated_grade = models.CharField(max_length=2)

    class Meta:
        db_table = 'GradeChallenge'
        managed = True