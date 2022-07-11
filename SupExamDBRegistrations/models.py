from django.contrib.auth.models import User
from django.db import models
from pkg_resources import Distribution
from superintendent.constants import DEPARTMENTS, SEMS, YEARS
from superintendent.models import MarksDistribution 


# class ProgrammeModel(models.Model):
#     PID = models.IntegerField(primary_key=True)
#     ProgrammeName = models.CharField(max_length=20)
#     ProgrammeType = models.CharField(max_length=10)
#     Specialization = models.CharField(max_length=100)
#     Dept = models.IntegerField()
#     class Meta:
#         db_table = 'ProgrammeModel'
#         managed = False

# class StudentInfo(models.Model):
#     CYCLE_CHOICES = (
#         (10,'PHYSICS'),
#         (9,'CHEMISTRY')
#     )
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     Regulation = models.IntegerField()
#     Dept = models.IntegerField()
#     AdmissionYear = models.IntegerField()
#     Gender = models.CharField(max_length=10)
#     Category = models.CharField(max_length=20)
#     GuardianName = models.CharField(max_length=50)
#     Phone = models.IntegerField()
#     email = models.CharField(max_length=50)
#     Address1 = models.CharField(max_length=150)
#     Address2 = models.CharField(max_length=100, null=True)
#     Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)

#     class Meta:
#         db_table = 'StudentInfo'
#         managed = False


        
# class RegistrationStatus(models.Model):
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Regulation = models.IntegerField()
#     Dept = models.IntegerField()
#     Mode = models.CharField(max_length=1) # R for Regular B for Backlog
#     Status = models.IntegerField()
#     class Meta:
#         db_table = 'Registration_Status'
#         managed = False

#     def __str__(self):
#         name =  str(DEPARTMENTS[self.Dept-1]) + ':' + str(YEARS[self.BYear]) + ':' + str(SEMS[self.BSem]) + ':' + \
#             str(self.AYear) + ':' + str(self.ASem) + ':' + str(self.Regulation) + ':' + str(self.Mode)
#         return name

# class RollLists(models.Model):
#     CYCLE_CHOICES = (
#         (10,'PHYSICS'),
#         (9,'CHEMISTRY')
#     )
#     student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     RegEventId = models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
#     Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
#     Section = models.CharField(max_length=2, default='NA')
#     class Meta:
#         db_table = 'RollLists'
#         unique_together = ('student', 'RegEventId')
#         managed = False
    
# class RollLists_Staging(models.Model):
#     CYCLE_CHOICES = (
#         (10,'PHYSICS'),
#         (9,'CHEMISTRY')
#     )
#     student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     RegEventId = models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
#     Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
#     Section = models.CharField(max_length=2, default='NA')
#     class Meta:
#         db_table = 'RollLists_Staging'
#         unique_together = ('student', 'RegEventId')
#         managed = False
        
# Create your models here.
# class StudentRegistrations(models.Model):
#     RegNo = models.IntegerField()
#     RegEventId = models.IntegerField()
#     Mode = models.IntegerField()
#     sub_id = models.IntegerField()
#     class Meta:
#         db_table = 'StudentRegistrations'
#         managed =False

# class StudentRegistrations_Staging(models.Model):
#     RegNo = models.IntegerField()
#     RegEventId = models.IntegerField()
#     Mode = models.IntegerField()
#     sub_id = models.IntegerField()
#     class Meta:
#         db_table = 'StudentRegistrations_Staging'
#         managed =False





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

# class StudentBacklogs(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     sub_id = models.IntegerField()
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=50)
#     OfferedYear = models.IntegerField()
#     Dept = models.IntegerField()
#     Credits = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     GP = models.IntegerField()
#     Regulation = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     class Meta:
#         db_table = 'StudentBacklogsMV'
#         managed = False
#     def __str__(self):        
#         return f'{self.SubName} ({self.SubCode})'

# class StudentMakeups(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     sub_id = models.IntegerField()
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=50)
#     OfferedYear = models.IntegerField()
#     Dept = models.IntegerField()
#     Credits = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     GP = models.IntegerField()
#     Regulation = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     class Meta:
#         db_table = 'StudentMakeupBacklogsMV'
#         managed = False

class CurrentAcademicYear(models.Model):
    AcademicYear=models.IntegerField()
    class Meta:
        db_table='CurrentAcademicYear'
        managed=False

# class SubjectFacultyInfo(models.Model):
#     SubId = models.IntegerField()
#     Section = models.CharField(max_length=10)
#     FacultyId = models.IntegerField()
#     class Meta:
#         db_table = 'SubjectFacultyInfo'
#         managed = False

# class FacultyInfo(models.Model):
#     FacultyId = models.IntegerField(default=100)
#     Name = models.CharField(max_length=100)
#     Phone = models.IntegerField()
#     Email = models.CharField(max_length=50)
#     Dept = models.IntegerField()
#     Working = models.BooleanField()
#     class Meta:
#         db_table = 'FacultyInfo'
#         managed = False



# class Subjects_Staging(models.Model):
#     SubCode = models.CharField(max_length=10) 
#     SubName= models.CharField(max_length=100)
#     # BYear = models.IntegerField()
#     # BSem = models.IntegerField()
#     # Dept =models.IntegerField()
#     # OfferedYear = models.IntegerField()
#     # Regulation = models.IntegerField()
#     Creditable = models.IntegerField()
#     Credits = models.IntegerField()
#     OfferedBy=models.IntegerField()
#     Type = models.CharField(max_length=10)
#     Category = models.CharField(max_length=10)
#     OfferedBy = models.IntegerField()
#     # RegEventId = models.IntegerField()
#     RegEventId = models.ForeignKey('SupExamDBRegistrations.RegistrationStatus', on_delete=models.CASCADE)
#     MarkDistribution = models.ForeignKey(MarksDistribution, on_delete=models.CASCADE)
#     DistributionRatio = models.TextField()

#     class Meta:
#         db_table = 'Subjects_Staging'
#         unique_together = ('SubCode', 'RegEventId')
#         managed = False


# class Subjects(models.Model):
#     SubCode = models.CharField(max_length=10) 
#     SubName= models.CharField(max_length=100)
#     # BYear = models.IntegerField()
#     # BSem = models.IntegerField()
#     # Dept =models.IntegerField()
#     # OfferedYear = models.IntegerField()
#     # Regulation = models.IntegerField()
#     Creditable = models.IntegerField()
#     Credits = models.IntegerField()
#     OfferedBy=models.IntegerField()
#     Type = models.CharField(max_length=10)
#     Category = models.CharField(max_length=10)
#     # OfferedBy = models.IntegerField()
#     # RegEventId = models.IntegerField()
#     RegEventId = models.ForeignKey('SupExamDBRegistrations.RegistrationStatus', on_delete=models.CASCADE)
#     MarkDistribution = models.ForeignKey(MarksDistribution, on_delete=models.CASCADE)
#     DistributionRatio = models.TextField()
    
#     class Meta:
#         db_table = 'Subjects'
#         unique_together = ('SubCode', 'RegEventId')
#         managed = False

#         # import_id_fields = ('id',)
#         # RegEventId = fields.Field(
#         #     column_name='id',
#         #     attribute='id',
#         #     widget=ForeignKeyWidget(RegistrationStatus, 'id')
#         # )
# class FacultyAssignment(models.Model):
#     subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, default=1)
#     Section = models.CharField(max_length=2, default='NA')
#     faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE, related_name='faculty_facultyInfo', default=0)
#     co_ordinator = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE, related_name='co_ordinator_facultyInfo', default=0)

#     class Meta:
#         db_table = 'FacultyAssignment'
#         managed = True


# class NotPromoted(models.Model):
#     AYear = models.IntegerField()
#     BYear = models.IntegerField()
#     Regulation = models.IntegerField()
#     student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     PoA = models.CharField(max_length=1) #S for Study Mode and R for Cancellation and Repeat
#     class Meta:
#         db_table = 'NotPromoted'
#         unique_together=('AYear', 'BYear', 'Regulation', 'student')
#         managed = False



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
        managed = False

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
        managed = False

# class StudentGrades(models.Model):
#     RegId= models.IntegerField()
#     RegEventId = models.IntegerField()
#     Regulation = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     AttGrade = models.CharField(max_length=2)
#     class Meta:
#         db_table = 'StudentGrades'
#         managed = False

# class StudentGrades_Staging(models.Model):
#     RegId = models.IntegerField()
#     RegEventId = models.IntegerField()
#     Regulation = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     AttGrade = models.CharField(max_length=2)
#     class Meta:
#         db_table = 'StudentGrades_Staging'
#         managed = False



# class StudentGradePoints(models.Model):
#     RegNo = models.IntegerField()
#     sub_id = models.IntegerField()
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=100)
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     OfferedYear = models.IntegerField()
#     Dept = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     AttGrade = models.CharField(max_length=2)
#     Regulation = models.IntegerField()
#     Creditable = models.IntegerField()
#     Credits = models.IntegerField()
#     Type = models.CharField(max_length=10)
#     Category = models.CharField(max_length=10)
#     Points = models.IntegerField()
#     GP = models.IntegerField()
#     AYASBYBS = models.IntegerField()
#     class Meta:
#         db_table = 'StudentGradePointsMV'
#         managed = False

class BranchChanges(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    CurrentDept = models.IntegerField()
    NewDept = models.IntegerField()
    AYear = models.IntegerField()
    class Meta:
        db_table = 'BranchChanges'
        managed = False

# class RegularRegistrationSummary(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Dept = models.IntegerField()
#     Regulation = models.IntegerField()
#     RegisteredSubjects = models.CharField(max_length=300)
#     class Meta:
#         db_table = 'RegularRegistrationSummaryV'
#         managed = False

# class BacklogRegistrationSummary(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Dept = models.IntegerField()
#     Regulation = models.IntegerField()
#     RegisteredSubjects = models.CharField(max_length=300)
#     class Meta:
#         db_table = 'BacklogRegistrationSummaryV'
#         managed = False

# class MakeupRegistrationSummary(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Dept = models.IntegerField()
#     Regulation = models.IntegerField()
#     RegisteredSubjects = models.CharField(max_length=300)
#     class Meta:
#         db_table = 'MakeupRegistrationSummaryV'
#         managed = False

# class Regulation(models.Model):
#     AdmissionYear = models.IntegerField()
#     AYear = models.IntegerField()
#     BYear = models.IntegerField()
#     Regulation = models.IntegerField()
#     class Meta:
#         db_table = 'Regulation'
#         managed = False

# class DroppedRegularCourses(models.Model):
#     student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
#     class Meta:
#         db_table = 'DroppedRegularCourses'
#         managed = False
    
# class MandatoryCredits(models.Model):
#     Regulation = models.IntegerField()
#     Dept = models.IntegerField()
#     BYear = models.IntegerField()
#     Credits = models.IntegerField()
#     class Meta:
#         db_table = 'MandatoryCredits'
#         managed = False

# class GradePoints(models.Model):
#     Regulation = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     Points = models.IntegerField()
#     class Meta:
#         db_table = 'GradePoints'
#         managed = False


# class GradeChallenge(models.Model):
#     RegId = models.IntegerField()
#     PreviousGrade = models.CharField(max_length=2)
#     UpdatedGrade = models.CharField(max_length=2)
#     class Meta:
#         db_table = 'GradeChallenge'
#         managed = False


# class RegulationChange(models.Model):
#     RegEventId= models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
#     student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     PreviousRegulation = models.IntegerField()
#     PresentRegulation = models.IntegerField()
#     class Meta:
#         db_table  = 'RegulationChange'
#         managed = False

# class NotRegistered(models.Model):
#     RegEventId= models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
#     student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     class Meta:
#         db_table = 'NotRegistered'
#         managed = False

class SeatCancellationInfo(models.Model):
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
    cancelled_on = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'SeatCancellationInfo'
        managed = False

class CancelledSeatRegistrations(models.Model):
    RegNo = models.IntegerField()
    RegEventId = models.IntegerField()
    Mode = models.IntegerField()
    sub_id = models.IntegerField()
    class Meta:
        db_table = 'CancelledSeatRegistrations'
        unique_together=('RegNo', 'RegEventId', 'sub_id')
        managed = False

class CancelledSeatGrades(models.Model):
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'CancelledSeatGrades'
        unique_together=('RegId', 'Grade')
        managed = False


# from django.contrib.auth import get_user_model
# User = get_user_model()
# class Faculty_user(models.Model):
#     User= models.ForeignKey(User, on_delete=models.CASCADE)
#     Faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)
#     AssignDate = models.DateField(auto_now_add=True)
#     RevokeDate = models.DateField(null=True)
#     class Meta:
#         db_table = 'Faculty_user'
#         managed = True


# class Faculty_Coordinator(models.Model):
#     User= models.ForeignKey(User, on_delete=models.CASCADE
#     )
#     Faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)
#     AssignDate = models.DateField(auto_now_add=True)
#     RevokeDate = models.DateField(null=True)
#     class Meta:
#         db_table = 'Faculty_Coordinator'
        
#         managed = True


# class Attendance_Shortage(models.Model):
#     Student = models.ForeignKey(StudentInfo, on_delete=models.CASCADE)
#     RegEventId =models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
#     Subject = models.ForeignKey(Subjects,on_delete=models.CASCADE)

#     class Meta:
#         db_table = 'Attendance_Shortage'
#         managed = True

# class PartialSeatCancellation(models.Model):
#     CYCLE_CHOICES = (
#         (10,'PHYSICS'),
#         (9,'CHEMISTRY')
#     )
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     Regulation = models.IntegerField()
#     Dept = models.IntegerField()
#     AdmissionYear = models.IntegerField()
#     Gender = models.CharField(max_length=10)
#     Category = models.CharField(max_length=20)
#     GuardianName = models.CharField(max_length=50)
#     Phone = models.IntegerField()
#     email = models.CharField(max_length=50)
#     Address1 = models.CharField(max_length=150)
#     Address2 = models.CharField(max_length=100, null=True)
#     Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
#     cancelled_on = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table = 'PartialSeatCancellation'
#         managed = False

# class PermanantSeatCancellation(models.Model):
#     CYCLE_CHOICES = (
#         (10,'PHYSICS'),
#         (9,'CHEMISTRY')
#     )
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     Name = models.CharField(max_length=70)
#     Regulation = models.IntegerField()
#     Dept = models.IntegerField()
#     AdmissionYear = models.IntegerField()
#     Gender = models.CharField(max_length=10)
#     Category = models.CharField(max_length=20)
#     GuardianName = models.CharField(max_length=50)
#     Phone = models.IntegerField()
#     email = models.CharField(max_length=50)
#     Address1 = models.CharField(max_length=150)
#     Address2 = models.CharField(max_length=100, null=True)
#     Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
#     cancelled_on = models.DateTimeField(auto_now_add=True)
#     class Meta:
#         db_table = 'PartialSeatCancellation'
#         managed = False

# class PartialSeatCancelledRegistrations(models.Model):




