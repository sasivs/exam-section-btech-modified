from django.db import models
from django.contrib.auth import get_user_model
from SupExamDBRegistrations.models import FacultyInfo, StudentRegistrations

# Create your models here.

User = get_user_model()

class HOD(models.Model):
    Faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)
    Dept = models.IntegerField()
    AssignedDate = models.DateTimeField(auto_now_add=True)
    RevokedDate = models.DateTimeField(null=True)
    User = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'HOD'
        unique_together = ('Faculty', 'Dept', 'AssignedDate')
        managed = True

class Departments(models.Model):
    Dept = models.IntegerField()
    Name = models.CharField(max_length=255)
    Dept_Code = models.CharField(max_length=255)

    class Meta:
        db_table = 'Departments'
        unique_together = ('Dept', 'Name', 'Dept_Code')
        managed = True

class MarksDistribution(models.Model):
    Distribution = models.CharField()
    DistributionNames=models.CharField()

    class Meta:
        db_table = 'MarksDistribution'
        unique_together = ('Distribution', 'DistributionNames')
        managed = True

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