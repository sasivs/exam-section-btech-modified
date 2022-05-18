from audioop import maxpp
from django.contrib.auth.models import User
from import_export import resources
from django.db import models

        
# Create your models here.
class StudentRegistrations(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.IntegerField()
    BSem = models.IntegerField()
    Mode = models.IntegerField() # 0 is exam mode and 1 is study mode
    class Meta:
        db_table = 'StudentRegistrations'
        managed =False

class ProgrammeModel(models.Model):
    PID = models.IntegerField(primary_key=True)
    ProgrammeName = models.CharField(max_length=20)
    ProgrammeType = models.CharField(max_length=10)
    Specialization = models.CharField(max_length=100)
    Dept = models.IntegerField()
    class Meta:
        db_table = 'Departments'
        managed = False

class StudentRegistrationsResource(resources.ModelResource):
    class Meta:
        model = StudentRegistrations 

class RegistrationStatus(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Mode = models.CharField(max_length=1) # R for Regular B for Backlog
    Status = models.IntegerField()
    class Meta:
        db_table = 'RegistrationStatus'
        managed = False

class MakeupSummaryStats(models.Model):
    SubName = models.CharField(max_length=100)
    SubCode = models.CharField(max_length=10)
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    BYear = models.IntegerField()
    Passed = models.IntegerField()
    Failed = models.IntegerField()
    Total = models.IntegerField()
    class Meta:
        db_table = 'MakeupSummaryStatsV'
        managed = False

class StudentMakeupBacklogsVsRegistrations(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    MakeupSubjects = models.CharField(max_length=300)
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'StudentMakeupBacklogsVsRegistrationsV'
        managed = False 

class StudentBacklogs(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    # Name = models.CharField(max_length=70)
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    Regulation = models.IntegerField()
    AYASBYBS = models.IntegerField()
    class Meta:
        db_table = 'StudentBacklogsMV'
        managed = False
    def __str__(self):        
        return f'{self.SubName} ({self.SubCode})'

class CurrentAcademicYear(models.Model):
    AcademicYear=models.IntegerField()
    class Meta:
        db_table='CurrentAcademicYear'
        managed=False

class StudentInfo(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=20)
    GaurdianName = models.CharField(max_length=50)
    Phone = models.IntegerField()
    email = models.CharField(max_length=50)
    Address1 = models.CharField(max_length=150)
    Address1 = models.CharField(max_length=100)
    class Meta:
        db_table = 'StudentInfo'
        managed = False


class Subjects_Staging(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept =models.IntegerField()
    OfferedYear = models.IntegerField()
    Regulation = models.IntegerField()
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    class Meta:
        db_table = 'Subjects_Staging'
        managed = False

class Subjects(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept =models.IntegerField()
    OfferedYear = models.IntegerField()
    Regulation = models.IntegerField()
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    class Meta:
        db_table = 'Subjects'
        managed = False


class SubjectStagingResource(resources.ModelResource):
    class Meta:
        model = Subjects_Staging 

class NotPromoted(models.Model):
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    RegNo = models.IntegerField()
    PoA = models.CharField(max_length=1) #S for Study Mode and R for Cancellation and Repeat
    class Meta:
        db_table = 'NotPromoted'
        managed = False

class StudentCancellation(models.Model):
    RegNo = models.IntegerField()
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2,null=True)
    class Meta:
        db_table = 'StudentCancellation'
        managed = True

class CancelledStudentInfo(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=20)
    GaurdianName = models.CharField(max_length=50)
    Phone = models.IntegerField()
    email = models.CharField(max_length=50)
    Address1 = models.CharField(max_length=150)
    Address2 = models.CharField(max_length=100,null=True)
    class Meta:
        db_table = 'CancelledStudentInfo'
        managed = True

class StudentGrades(models.Model):
    RegNo = models.IntegerField()
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'StudentGrades'
        managed = False

class StudentGradePoints(models.Model):
    RegNo = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    Credits = models.IntegerField()
    AYASBYBS = models.IntegerField()
    Type = models.CharField(max_length=10)
    class Meta:
        db_table = 'StudentGradePointsMV'
        managed = False

class BranchChanges(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    CurrentDept = models.IntegerField()
    NewDept = models.IntegerField()
    AYear = models.IntegerField()
    class Meta:
        db_table = 'BranchChanges'
        managed = True

class RegularRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'RegularRegistrationSummaryV'
        managed = False

class BacklogRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    Dept = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'BacklogRegistrationSummaryV'
        managed = False
