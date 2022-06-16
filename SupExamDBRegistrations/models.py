from audioop import maxpp
from pyexpat import model
# from typing_extensions import Required
from django.contrib.auth.models import User
from import_export import resources
from django.db import models


        
# Create your models here.
class StudentRegistrations(models.Model):
    RegNo = models.IntegerField()
    RegEventId = models.IntegerField()
    Mode = models.IntegerField()
    sub_id = models.IntegerField()
    class Meta:
        db_table = 'StudentRegistrations'
        managed =False

class StudentRegistrations_Staging(models.Model):
    RegNo = models.IntegerField()
    RegEventId = models.IntegerField()
    Mode = models.IntegerField()
    sub_id = models.IntegerField()
    class Meta:
        db_table = 'StudentRegistrations_Staging'
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
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    Mode = models.CharField(max_length=1) # R for Regular B for Backlog
    Status = models.IntegerField()
    class Meta:
        db_table = 'Registration_Status'
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
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.IntegerField()
    AYASBYBS = models.IntegerField()
    class Meta:
        db_table = 'StudentBacklogsMV'
        managed = False
    def __str__(self):        
        return f'{self.SubName} ({self.SubCode})'

class StudentMakeups(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    sub_id = models.IntegerField()
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=50)
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Credits = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Grade = models.CharField(max_length=2)
    GP = models.IntegerField()
    Regulation = models.IntegerField()
    AYASBYBS = models.IntegerField()
    class Meta:
        db_table = 'StudentMakeupBacklogsMV'
        managed = False

class CurrentAcademicYear(models.Model):
    AcademicYear=models.IntegerField()
    class Meta:
        db_table='CurrentAcademicYear'
        managed=False

class SubjectFacultyInfo(models.Model):
    SubId = models.IntegerField()
    Section = models.CharField(max_length=10)
    FacultyId = models.IntegerField()
    class Meta:
        db_table = 'SubjectFacultyInfo'
        managed = False

class FacultyInfo(models.Model):
    Name = models.CharField(max_length=100)
    Phone = models.IntegerField()
    Email = models.CharField(max_length=50)
    class Meta:
        db_table = 'FacultyInfo'
        managed = False

class StudentInfo(models.Model):
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
    Address2 = models.CharField(max_length=100)
    Cycle = models.IntegerField()
    FirstYearSection = models.CharField(max_length=10)
    NonFirstYearSection = models.CharField(max_length=10)
    class Meta:
        db_table = 'StudentInfo'
        managed = False

class StudentInfoResource(resources.ModelResource):
    class Meta:
        model = StudentInfo 

class RollLists(models.Model):
    RegNo = models.IntegerField()
    Dept = models.IntegerField()
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Cycle = models.IntegerField()
    Regulation = models.IntegerField()
    class Meta:
        db_table = 'RollLists'
        managed = False
    
class RollLists_Staging(models.Model):
    RegNo = models.IntegerField()
    Dept = models.IntegerField()
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Cycle = models.IntegerField()
    Regulation = models.IntegerField()
    class Meta:
        db_table = 'RollLists_Staging'
        managed = False

class Subjects_Staging(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    # BYear = models.IntegerField()
    # BSem = models.IntegerField()
    # Dept =models.IntegerField()
    # OfferedYear = models.IntegerField()
    # Regulation = models.IntegerField()
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    RegEventId = models.IntegerField()
    class Meta:
        db_table = 'Subjects_Staging'
        managed = False

class Subjects(models.Model):
    SubCode = models.CharField(max_length=10) 
    SubName= models.CharField(max_length=100)
    # BYear = models.IntegerField()
    # BSem = models.IntegerField()
    # Dept =models.IntegerField()
    # OfferedYear = models.IntegerField()
    # Regulation = models.IntegerField()
    Creditable = models.IntegerField()
    Credits = models.IntegerField()
    Type = models.CharField(max_length=10)
    Category = models.CharField(max_length=10)
    RegEventId = models.IntegerField()
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
class NotPromotedResource(resources.ModelResource):
    class Meta:
        model = NotPromoted


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
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'StudentGrades'
        managed = False

class StudentGrades_Staging(models.Model):
    RegId = models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'StudentGrades_Staging'
        managed = False

class StudentGrades_StagingResource(resources.ModelResource):
    class Meta:
        model = StudentGrades_Staging

class StudentGradePoints(models.Model):
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
    Regulation = models.IntegerField()
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
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'BacklogRegistrationSummaryV'
        managed = False

class MakeupRegistrationSummary(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    RegisteredSubjects = models.CharField(max_length=300)
    class Meta:
        db_table = 'MakeupRegistrationSummaryV'
        managed = False

class Regulation(models.Model):
    AdmissionYear = models.IntegerField()
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.IntegerField()
    class Meta:
        db_table = 'Regulation'
        # managed = False

class DroppedRegularCourses(models.Model):
    RegNo = models.IntegerField()
    sub_id = models.IntegerField()
    class Meta:
        db_table = 'DroppedRegularCourses'
        managed = False
    
class MandatoryCredits(models.Model):
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    Credits = models.IntegerField()
    class Meta:
        db_table = 'MandatoryCredits'
        managed = False

class GradePoints(models.Model):
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    Points = models.IntegerField()
    class Meta:
        db_table = 'GradePoints'
        managed = False
class GradePointsResource(resources.ModelResource):
    class Meta:
        model = GradePoints

class GradeChallenge(models.Model):
    RegId = models.IntegerField()
    PreviousGrade = models.CharField(max_length=2)
    UpdatedGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'GradeChallenge'
        managed = True
class GradeChallengeResource(resources.ModelResource):
    class Meta:
        model = GradeChallenge

