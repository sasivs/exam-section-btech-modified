from django.db import models

from django.db import models
from MTco_ordinator.models import MTStudentRegistrations

# Create your models here.

class MTStudentInfo(models.Model):
    RegNo = models.IntegerField()
   # RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    AdmissionYear=models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=20)
    GuardianName = models.CharField(max_length=50)
    Phone = models.IntegerField()
    email = models.CharField(max_length=50)
    Address1 = models.CharField(max_length=150)
    Address2 = models.CharField(max_length=100, null=True)
    
    class Meta:
        db_table = 'MTStudentInfo'
        constraints = [
            models.UniqueConstraint(fields=['RegNo'], name='unique_StudentInfo_RegNo'),
        ]
        managed = True



class MTIXGradeStudents(models.Model):
    GRADE_CHOICES = (
        ('I', 'I'),
        ('X', 'X')
    )
    Registration = models.ForeignKey(MTStudentRegistrations, on_delete=models.CASCADE)
    Grade = models.CharField(max_length=1, choices=GRADE_CHOICES)

    class Meta:
        db_table = 'MTIXGradeStudents'
        unique_together = ('Registration', 'Grade')
        managed = True

class MTFacultyInfo(models.Model):
    FacultyId = models.IntegerField(default=100)
    Name = models.CharField(max_length=100)
    Phone = models.IntegerField()
    Email = models.CharField(max_length=50)
    Dept = models.IntegerField()
    Working = models.BooleanField()
    class Meta:
        db_table = 'MTFacultyInfo'
        constraints = [
            models.UniqueConstraint(fields=['FacultyId'], name='unique_facultyinfo_facultyid')
        ]
        managed = True

