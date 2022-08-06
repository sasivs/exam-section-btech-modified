
from django.db import models

# Create your models here.
from django.db import models
from django.db.models.base import Model

# Create your models here.



class BTDegreeAwardees(models.Model):
    RegNo=models.IntegerField()
    RollNo=models.IntegerField()
    Dept=models.IntegerField()
    Name=models.CharField(max_length=70)
    PassingYear=models.IntegerField()
    Regulation = models.IntegerField()
    Degree = models.CharField(max_length=30)
    class Meta:
        db_table = 'BTDegreeAwardees'
        managed = True

class BTStudentGradePointsV(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    Grade = models.CharField(max_length=2)
    Credits = models.IntegerField()
    AYASBYBS = models.IntegerField()
    Type = models.CharField(max_length=10)
    Order = models.IntegerField()
    class Meta:
        db_table = 'BTStudentGradePointsV'
        managed = False

class BTDepartmentExamEvents(models.Model):
    Dept = models.IntegerField()
    AYASBYBS = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    class Meta:
        db_table = 'BTDeptExamEventsMV'
        managed = False


class BTStudentExamEvents(models.Model):
    RegNo = models.IntegerField()
    AYASBYBS = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    IsRegular = models.IntegerField()
    class Meta:
        db_table = 'BTStudentExamEventsMV'
        managed = False


class BTDeptExamEventStudents(models.Model):
    Dept = models.IntegerField()
    AYASBYBS = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    class Meta:
        db_table = 'BTDeptExamEventStudentsMV'
        managed = False



class BTStudentCGPAs(models.Model):
    RegNo = models.IntegerField()
    AYASBYBS_G = models.IntegerField()
    CGP = models.IntegerField()
    CC = models.IntegerField()
    CGPA = models.FloatField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'BTStudentCGPAsMV'
        managed = False


class BTStudentBestGrades(models.Model):
    RegNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    Regulation = models.IntegerField()
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    Points = models.IntegerField()
    GP = models.IntegerField()
    AYASBYBS = models.IntegerField()
    Required = models.IntegerField()
    # Order = models.IntegerField()
    class Meta:
        db_table = 'BTStudentBestGradesV'
        managed = False

class BTStudentFinalSGPAs(models.Model):
    RegNo = models.IntegerField()
    BYBS = models.IntegerField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'BTStudentFinalSGPAsV'
        managed = False

class BTStudentFinalCGPA(models.Model):
    RegNo = models.IntegerField()
    CGP = models.IntegerField()
    TotalCredits = models.IntegerField()
    CGPA = models.FloatField()
    class Meta:
        db_table = 'BTStudentFinalCGPAV'
        managed = False




#MTech Models


class MTDegreeAwardees(models.Model):
    RegNo=models.IntegerField()
    Dept=models.IntegerField()
    Name=models.CharField(max_length=70)
    PassingYear=models.IntegerField()
    Regulation = models.IntegerField()
    Degree = models.CharField(max_length=30)
    class Meta:
        db_table = 'MTDegreeAwardees'
        managed = True

class MTStudentGradePointsV(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    Grade = models.CharField(max_length=2)
    Credits = models.IntegerField()
    AYASMYMS = models.IntegerField()
    Type = models.CharField(max_length=10)
    Order = models.IntegerField()
    class Meta:
        db_table = 'MTStudentGradePointsV'
        managed = False

class MTDepartmentExamEvents(models.Model):
    Dept = models.IntegerField()
    AYASMYMS = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    class Meta:
        db_table = 'MTDeptExamEventsMV'
        managed = False


class MTStudentExamEvents(models.Model):
    RegNo = models.IntegerField()
    AYASMYMS = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    IsRegular = models.IntegerField()
    class Meta:
        db_table = 'MTStudentExamEventsMV'
        managed = False


class MTDeptExamEventStudents(models.Model):
    Dept = models.IntegerField()
    AYASMYMS = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    RegNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    class Meta:
        db_table = 'MTDeptExamEventStudentsMV'
        managed = False



class MTStudentCGPAs(models.Model):
    RegNo = models.IntegerField()
    AYASMYMS_G = models.IntegerField()
    CGP = models.IntegerField()
    CC = models.IntegerField()
    CGPA = models.FloatField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'MTStudentCGPAsMV'
        managed = False

###########################################################


# class StudentGradePointsV(models.Model):
#     RegNo = models.IntegerField()
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=100)
#     Grade = models.CharField(max_length=2)
#     Credits = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     Type = models.CharField(max_length=10)
#     Order = models.IntegerField()
#     class Meta:
#         db_table = 'StudentGradePointsV'
#         managed = False

# class BTStudentInfo(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     Dept = models.IntegerField()
#     class Meta:
#         db_table = 'BTStudentInfo'
#         managed = False


# class StudentAdmissionYearDetails(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     Dept = models.IntegerField()
#     AdmissionYear = models.IntegerField()
#     class Meta:
#         db_table = 'StudentAdmissionInfoV'
#         managed = False 

# class StudentSemSubCounts(models.Model):
#     RegNo=models.IntegerField()
#     BYBS=models.IntegerField()
#     SemSubCount=models.IntegerField()
#     class Meta:
#         db_table = 'StudentSemSubCountsV'
#         managed = False

