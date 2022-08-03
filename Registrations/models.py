from django.db import models
from django.db.models import manager
# Create your models here.
# class StudentMakeupBacklogs(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     # Name = models.CharField(max_length=70)
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=50)
#     OfferedYear = models.IntegerField()
#     Dept = models.IntegerField()
#     Credits = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     Regulation = models.IntegerField()
#     AYASBYBS = models.IntegerField()
    
#     class Meta:
#         db_table = 'StudentMakeupBacklogsMV'
#         managed = False 
#     def __str__(self):        
#         return f'{self.SubName} ({self.SubCode})'
# class StudentRegistrations(models.Model):
#     RegNo = models.IntegerField()
#     SubCode = models.CharField(max_length=10)
#     AYear = models.IntegerField()
#     ASem = models.IntegerField()
#     OfferedYear = models.IntegerField()
#     Dept = models.IntegerField()
#     BYear = models.IntegerField()
#     Regulation = models.IntegerField()
#     BSem = models.IntegerField()
#     Mode = models.IntegerField() # 0 is exam mode and 1 is study mode
#     class Meta:
#         db_table = 'StudentRegistrations'

class CurrentAcademicYear(models.Model):
    AcademicYear=models.IntegerField()
    class Meta:
        db_table='CurrentAcademicYear'
        managed=False

class CoordinatorInfo(models.Model):
    UserId = models.CharField(max_length=30)
    Dept = models.IntegerField()
    Year = models.IntegerField()
    ProgramType = models.CharField(max_length=10)
    class Meta:
        db_table = 'CoordinatorInfo'
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
class CoordinatorMakeupRegNos(models.Model):
    BYear = models.IntegerField()
    Dept = models.IntegerField()
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    BSem = models.IntegerField()
    class Meta:
        db_table = 'CoordinatorMakeupRegNosV'
        managed = False

class CoordinatorBacklogRegNos(models.Model):
    BYear = models.IntegerField()
    Dept = models.IntegerField()
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    BSem = models.IntegerField()
    class Meta:
        db_table = 'CoordinatorBacklogRegNosV'
        managed = False

class CoordinatorMakeupSubCodesV(models.Model):
    RegNo = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()    
    SubCode = models.CharField(max_length=10)
    SubName = models.CharField(max_length=100)
    Regulation = models.IntegerField()
    class Meta:
        db_table = 'CoordinatorMakeupSubCodesV'
        managed = False
    
class StudentMakeupMarks(models.Model):
    RegNo = models.IntegerField() #models.ForeignKey(BTStudentInfo, on_delete=models.CASCADE, to_field='RegNo')
    SubCode = models.CharField(max_length=10)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    Marks= models.IntegerField()
    Status = models.BooleanField(default=False)
    Grade = models.CharField(max_length=2)
    Regulation = models.IntegerField()
    class Meta:
        db_table = "StudentMakeupMarks"  

class StudentMakeupMarksDetails(models.Model):
    RegNo = models.IntegerField() #models.ForeignKey(StudentInfo, on_delete=models.CASCADE, to_field='RegNo')
    RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    SubCode = models.CharField(max_length=10)
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    OfferedYear = models.IntegerField()
    Dept = models.IntegerField()
    Regulation = models.IntegerField()
    BYear = models.IntegerField()
    Marks= models.IntegerField()
    Status = models.BooleanField(default=False)
    Grade = models.CharField(max_length=2)
    class Meta:
        db_table = "StudentMakeupMarksDetailsV"

class Coordinator1Info(models.Model):
    UserId = models.CharField(max_length=30)
    Dept = models.IntegerField()
    Year = models.IntegerField()
    Sem = models.IntegerField()
    ProgramType = models.CharField(max_length=10)
    class Meta:
        db_table = 'Coordinator1Info'
        managed = False 

# class BTStudentBacklogs(models.Model):
#     RegNo = models.IntegerField()
#     RollNo = models.IntegerField()
#     # Name = models.CharField(max_length=70)
#     SubCode = models.CharField(max_length=10)
#     SubName = models.CharField(max_length=50)
#     OfferedYear = models.IntegerField()
#     Dept = models.IntegerField()
#     Credits = models.IntegerField()
#     BYear = models.IntegerField()
#     BSem = models.IntegerField()
#     Grade = models.CharField(max_length=2)
#     Regulation = models.IntegerField()
#     AYASBYBS = models.IntegerField()
    
#     class Meta:
#         db_table = 'StudentBacklogsMV'
#         managed = False 
#     def __str__(self):        
#         return f'{self.SubName} ({self.SubCode})'