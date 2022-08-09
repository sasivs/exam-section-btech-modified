from django.db import models

from django.db import models
from MTco_ordinator.models import MTStudentRegistrations

# Create your models here.

class MTStudentInfo(models.Model):
    RegNo = models.IntegerField()
   # RollNo = models.IntegerField()
    Name = models.CharField(max_length=255)
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    AdmissionYear = models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=30)
    GuardianName = models.CharField(max_length=255)
    Phone = models.TextField()
    email = models.TextField()
    Address1 = models.TextField()
    Address2 = models.TextField(null=True)
    
    class Meta:
        db_table = 'MTStudentInfo'
        constraints = [
            models.UniqueConstraint(fields=['RegNo'], name='unique_MTStudentInfo_RegNo'),
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
    Name = models.CharField(max_length=255)
    Phone = models.TextField()
    Email = models.CharField(max_length=525)
    Dept = models.IntegerField()
    Working = models.BooleanField()
    class Meta:
        db_table = 'MTFacultyInfo'
        constraints = [
            models.UniqueConstraint(fields=['FacultyId'], name='unique_MTfacultyinfo_facultyid')
        ]
        managed = True

