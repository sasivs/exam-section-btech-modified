from django.db import models
from co_ordinator.models import StudentRegistrations

# Create your models here.

class StudentInfo(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    AdmissionYear = models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=20)
    GuardianName = models.CharField(max_length=50)
    Phone = models.IntegerField()
    email = models.CharField(max_length=50)
    Address1 = models.CharField(max_length=150)
    Address2 = models.CharField(max_length=100, null=True)
    Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)

    class Meta:
        db_table = 'StudentInfo'
        managed = False


class IXGradeStudents(models.Model):
    GRADE_CHOICES = (
        ('I', 'I'),
        ('X', 'X')
    )
    Registration = models.ForeignKey(StudentRegistrations, on_delete=models.CASCADE)
    Grade = models.CharField(max_length=1, choices=GRADE_CHOICES)

    class Meta:
        db_table = 'IXGradeStudents'
        unique_together = ('Registration', 'Grade')
        managed = True
