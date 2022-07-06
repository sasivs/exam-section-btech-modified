from django.db import models
from SupExamDBRegistrations.models import StudentInfo, RegistrationStatus, Subjects
# Create your models here.

class Attendance_Shortage(models.Model):
    Student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
    RegEventId =models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
    Subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)

    class Meta:
        db_table = 'Attendance_Shortage'
        managed = True
