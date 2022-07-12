# from django.db import models
# from django.db.models.base import Model

# # Create your models here.

# class ProgrammeModel(models.Model):
#     PID = models.IntegerField(primary_key=True)
#     ProgrammeName = models.CharField(max_length=20)
#     ProgrammeType = models.CharField(max_length=10)
#     Specialization = models.CharField(max_length=100)
#     Dept = models.IntegerField()
#     class Meta:
#         db_table = 'Departments'
#         managed = False


# class DepartmentExamEvents(models.Model):
#     Dept = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     class Meta:
#         db_table = 'DeptExamEventsMV'
#         managed = False

# class StudentExamEvents(models.Model):
#     RegNo = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     IsRegular = models.IntegerField()
#     class Meta:
#         db_table = 'StudentExamEventsMV'
#         managed = False

# class DeptExamEventStudents(models.Model):
#     Dept = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     class Meta:
#         db_table = 'DeptExamEventStudentsMV'
#         managed = False

# class StudentGradePoints(models.Model):
#     RegNo = models.IntegerField()
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=100)
#     Grade = models.CharField(max_length=2)
#     Credits = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     class Meta:
#         db_table = 'StudentGradePointsMV'
#         managed = False

# class StudentInfo(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     class Meta:
#         db_table = 'StudentInfo'
#         managed = False

# class StudentCGPAs(models.Model):
#     RegNo = models.IntegerField()
#     AYASBYBS_G = models.IntegerField()
#     CGP = models.IntegerField()
#     CC = models.IntegerField()
#     CGPA = models.FloatField()
#     SGP = models.IntegerField()
#     SC = models.IntegerField()
#     SGPA = models.FloatField()
#     class Meta:
#         db_table = 'StudentCGPAsMV'
#         managed = False

# class HeldIn(models.Model):
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     HeldIn = models.CharField(max_length=10)
#     class Meta:
#         db_table = 'HeldIn'
#         managed = False 

# class StudentAdmissionYearDetails(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     Dept = models.IntegerField()
#     AdmissionYear = models.IntegerField()
#     class Meta:
#         db_table = 'StudentDetailsV'
#         managed = False 

