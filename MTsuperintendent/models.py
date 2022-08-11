from django.db import models
from django.contrib.auth import get_user_model
from MTco_ordinator.models import MTSubjects

# Create your models here.
User = get_user_model()

class MTRegulation(models.Model):
    
    AdmissionYear = models.IntegerField()
    AYear = models.IntegerField()
    MYear = models.IntegerField()
    Regulation = models.IntegerField()
    
    class Meta:
        db_table = 'MTRegulation'
        constraints = [
            models.UniqueConstraint(fields=['AdmissionYear', 'AYear', 'MYear'], name='unique_MTRegulation')
        ]
        managed = True


class MTProgrammeModel(models.Model):
    PID = models.IntegerField(primary_key=True)
    ProgrammeName = models.CharField(max_length=20)
    ProgrammeType = models.CharField(max_length=10)
    Specialization = models.CharField(max_length=100)
    Dept = models.IntegerField()
    class Meta:
        db_table = 'MTProgrammeModel'
        constraints=[
            models.UniqueConstraint(fields=['PID'],name='unique_MTPID')
        ]
        managed = True


class MTHOD(models.Model):
    Faculty = models.ForeignKey('MTExamStaffDB.MTFacultyInfo', on_delete=models.CASCADE)
    Dept = models.IntegerField()
    AssignedDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    User = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'MTHOD'
        unique_together = (('Faculty', 'Dept', 'AssignedDate'))
        managed = True

class MTDepartments(models.Model):
    Dept = models.IntegerField()
    Name = models.CharField(max_length=255)
    Dept_Code = models.CharField(max_length=255)

    class Meta:
        db_table = 'MTDepartments'
        unique_together = (('Dept', 'Name', 'Dept_Code'))
        managed = True

    

class MTMarksDistribution(models.Model):
    Distribution = models.TextField()
    DistributionNames=models.TextField()
    PromoteThreshold = models.TextField()

    class Meta:
        db_table = 'MTMarksDistribution'
        unique_together = (('Distribution', 'DistributionNames'))
        managed = True
    
    def distributions(self):
        distributions_names = self.DistributionNames.split(',')
        distributions_marks = self.Distribution.split(',')
        CHOICES = []
        outer_index = 0
        for names, marks in zip(distributions_names, distributions_marks):
            names = names.split('+')
            marks = marks.split('+')
            inner_index = 0
            for n,m in zip(names,marks):
                CHOICES += [(str(outer_index)+','+str(inner_index), str(n)+', '+str(m))]
                inner_index += 1
            outer_index += 1
        return CHOICES

    def get_zeroes_string(self):
        distribution_marks = self.Distribution.split(',')
        marks = [row.split('+') for row in distribution_marks]
        zero_marks = [['0' for mark in range(len(row))] for row in marks]
        zero_marks = ['+'.join(mark) for mark in zero_marks]
        zero_marks = ','.join(zero_marks)
        return zero_marks

    def get_marks_limit(self, outer, inner):
        return int(self.Distribution.split(',')[outer].split('+')[inner])

    def get_excel_column_index(self, outer, inner):
        distribution_marks = self.Distribution.split(',')
        marks = [row.split('+') for row in distribution_marks]
        index = 2
        '''
        index starts from 1 availing for the roll number(index=0) and name(index=1) rows in excel sheet.
        '''
        for num in range(outer):
            index += len(marks[num])
        index += inner
        return index



class MTGradePoints(models.Model):
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    Points = models.IntegerField()
    class Meta:
        db_table = 'MTGradePoints'
        unique_together = (('Regulation', 'Grade', 'Points'))
        managed = True


class MTCancelledStudentInfo(models.Model):
    CYCLE_CHOICES = (
        (10,'PHYSICS'),
        (9,'CHEMISTRY')
    )
    RegNo = models.IntegerField()
    # RollNo = models.IntegerField()
    Name = models.CharField(max_length=70)
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    AdmissionYear = models.IntegerField()
    Gender = models.CharField(max_length=10)
    Category = models.CharField(max_length=20)
    GuardianName = models.CharField(max_length=50)
    Phone = models.TextField()
    email = models.CharField(max_length=50)
    Address1 = models.CharField(max_length=150)
    Address2 = models.CharField(max_length=100, null=True)
    # Cycle = models.IntegerField(default=0, choices=CYCLE_CHOICES)
    CancelledDate = models.DateField()
    Remarks = models.TextField()

    class Meta:
        db_table = 'MTCancelledStudentInfo'
        constraints = [
            models.UniqueConstraint(fields=['RegNo'], name='unique_MTcancelled_StudentInfo_RegNo'),
        ]
        managed = True

class MTCancelledStudentRegistrations(models.Model):
    RegNo = models.IntegerField()
    RegEventId_id = models.IntegerField()
    Mode = models.IntegerField()
    sub_id_id = models.IntegerField()
    class Meta:
        db_table = 'MTCancelledStudentRegistrations'
        unique_together = (('RegNo', 'RegEventId_id', 'sub_id_id'))
        managed = True


class MTCancelledStudentGrades(models.Model):
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'MTCancelledStudentGrades'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_MTcancelled_StudentGrades_registration')
        ]
        managed = True

class MTCancelledRollLists(models.Model):
    student_id = models.IntegerField()
    RegEventId_id =models.IntegerField()
    class Meta:
        db_table = 'MTCancelledRollLists'
        unique_together = (('student_id', 'RegEventId_id'))
        managed = True

class MTCancelledNotRegistered(models.Model):
    RegEventId_id = models.IntegerField()
    Student_id = models.IntegerField()
    Registered = models.BooleanField()
    class Meta:
        db_table = 'MTCancelledNotRegistered'
        unique_together = (('RegEventId_id', 'Student_id'))
        managed = True


class MTCancelledMarks(models.Model):
    Registration_id = models.IntegerField()
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'MTCancelledMarks'
        constraints = [
            models.UniqueConstraint(fields=['Registration_id'], name='unique_MTcancelled_marks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = MTSubjects.objects.filter(id=self.Registration.sub_id).first()
        ratio = subject.DistributionRatio.split(':')
        total_parts = 0
        for part in ratio:
            total_parts += int(part)
        total = 0
        for index in range(len(marks_dis)):
            marks_row = marks_dis[index]
            sub_total = 0
            for mark in marks_row:
                sub_total += int(mark)
            total = sub_total*int(ratio[index])
        return round(total/total_parts)

class MTStudentCGPAs_Staging(models.Model):
    RegNo = models.IntegerField()
    AYASMYMS_G = models.IntegerField()
    CGP = models.IntegerField()
    CC = models.IntegerField()
    CGPA = models.FloatField()
    SGP = models.IntegerField()
    SC = models.IntegerField()
    SGPA = models.FloatField()
    class Meta:
        db_table = 'MTStudentCGPAs_StagingMV'
        managed = False


class MTHeldIn(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    MYear = models.IntegerField()
    MSem = models.IntegerField()
    AYASMYMS = models.IntegerField()
    HeldInMonth = models.CharField(max_length=10)
    HeldInYear = models.IntegerField()
    class Meta:
        db_table = 'MTHeldIn'
        constraints = [
            models.UniqueConstraint(fields=['AYASMYMS'], name='unique_ayasmyms_mtheldin')
        ]
        managed = True