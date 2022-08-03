
from django.db import models

# Create your models here.
from django.db import models
from django.db.models.base import Model

# Create your models here.

class BTProgrammeModel(models.Model):
    PID = models.IntegerField(primary_key=True)
    ProgrammeName = models.CharField(max_length=20)
    ProgrammeType = models.CharField(max_length=10)
    Specialization = models.CharField(max_length=100)
    Dept = models.IntegerField()
    class Meta:
        db_table = 'BTProgrammeModel'
        managed = False


class DepartmentExamEvents(models.Model):
    Dept = models.IntegerField()
    AYASBYBS = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    class Meta:
        db_table = 'DeptExamEventsMV'
        managed = False


class StudentExamEvents(models.Model):
    RegNo = models.IntegerField()
    AYASBYBS = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    IsRegular = models.IntegerField()
    class Meta:
        db_table = 'StudentExamEventsMV'
        managed = False


class DeptExamEventStudents(models.Model):
    Dept = models.IntegerField()
    AYASBYBS = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    class Meta:
        db_table = 'DeptExamEventStudentsMV'
        managed = False


class BTStudentGradePoints(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    Grade = models.CharField(max_length=2)
    Credits = models.IntegerField()
    AYASBYBS = models.IntegerField()
    Type = models.CharField(max_length=10)
    class Meta:
        db_table = 'StudentGradePointsMV'
        managed = False

class StudentGradePointsV(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    Grade = models.CharField(max_length=2)
    Credits = models.IntegerField()
    AYASBYBS = models.IntegerField()
    Type = models.CharField(max_length=10)
    Order = models.IntegerField()
    class Meta:
        db_table = 'StudentGradePointsV'
        managed = False

class BTStudentInfo(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Dept = models.IntegerField()
    class Meta:
        db_table = 'BTStudentInfo'
        managed = False


class StudentCGPAs(models.Model):
    RegNo = models.IntegerField()
    AYASBYBS_G = models.IntegerField()
    CGP = models.IntegerField()
    CC = models.IntegerField()
    CGPA = models.FloatField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'StudentCGPAsMV'
        managed = False


class HeldIn(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    AYASBYBS = models.IntegerField()
    HeldInMonth = models.CharField(max_length=10)
    HeldInYear = models.IntegerField()
    class Meta:
        db_table = 'HeldIn'
        managed = False 



class StudentAdmissionYearDetails(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Dept = models.IntegerField()
    AdmissionYear = models.IntegerField()
    class Meta:
        db_table = 'StudentAdmissionInfoV'
        managed = False 


class StudentSemSubCounts(models.Model):
    RegNo=models.IntegerField()
    BYBS=models.IntegerField()
    SemSubCount=models.IntegerField()
    class Meta:
        db_table = 'StudentSemSubCountsV'
        managed = False


class StudentBestGrades(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    Grade = models.CharField(max_length=2)
    Credits = models.IntegerField()
    Creditable = models.IntegerField()
    Category = models.CharField(max_length=10)
    AYASBYBS = models.IntegerField()
    BYBS = models.IntegerField()
    Required = models.IntegerField()
    Order = models.IntegerField()
    class Meta:
        db_table = 'StudentBestGradesV'
        managed = False

class StudentFinalSGPAs(models.Model):
    RegNo = models.IntegerField()
    BYBS = models.IntegerField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'StudentFinalSGPAsV'
        managed = False

class StudentFinalCGPA(models.Model):
    RegNo = models.IntegerField()
    CGP = models.IntegerField()
    TotalCredits = models.IntegerField()
    CGPA = models.FloatField()
    class Meta:
        db_table = 'StudentFinalCGPAV'
        managed = False

class DegreeAwardees(models.Model):
    RegNo=models.IntegerField()
    RollNo=models.IntegerField()
    Dept=models.IntegerField()
    Name=models.CharField(max_length=70)
    PassingYear=models.IntegerField()
    Regulation = models.IntegerField()
    Degree = models.CharField(max_length=30)
    class Meta:
        db_table='DegreeAwardees'
        managed=False

