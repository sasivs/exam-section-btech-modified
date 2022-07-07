from django.db import models
from SupExamDBRegistrations.models import StudentInfo, RegistrationStatus, Subjects, GradePoints
# Create your models here.

class Attendance_Shortage(models.Model):
    Student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    RegEventId =models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
    Subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)

    class Meta:
        db_table = 'Attendance_Shortage'
        managed = True

class GradesThreshold(models.Model):
    Grade = models.ForeignKey(GradePoints, on_delete=models.CASCADE)
    Subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
    Threshold_Mark = models.IntegerField()
    uniform_grading = models.BooleanField()
    Section = models.CharField(max_length=2, default='NA')
    class Meta:
        db_table = 'GradesThreshold'
        unique_together = ('Grade', 'subject', 'RegEventId', 'Section')
        managed = True