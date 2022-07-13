from enum import unique
from django.db import models
from django.contrib.auth import get_user_model
# from ExamStaffDB.models import FacultyInfo
from superintendent.constants import DEPARTMENTS, YEARS, SEMS

# Create your models here.

User = get_user_model()


class Regulation(models.Model):
    AdmissionYear = models.IntegerField()
    AYear = models.IntegerField()
    BYear = models.IntegerField()
    Regulation = models.IntegerField()
    class Meta:
        db_table = 'Regulation'
        constraints = [
            models.UniqueConstraint(fields=['AdmissionYear', 'AYear', 'BYear'], name='unique_Regulation')
        ]
        managed = True

class ProgrammeModel(models.Model):
    PID = models.IntegerField(primary_key=True)
    ProgrammeName = models.CharField(max_length=20)
    ProgrammeType = models.CharField(max_length=10)
    Specialization = models.CharField(max_length=100)
    Dept = models.IntegerField()
    class Meta:
        db_table = 'ProgrammeModel'
        managed = True

class RegistrationStatus(models.Model):
    AYear = models.IntegerField()
    ASem = models.IntegerField()
    BYear = models.IntegerField()
    BSem = models.IntegerField()
    Regulation = models.IntegerField()
    Dept = models.IntegerField()
    Mode = models.CharField(max_length=1) # R for Regular B for Backlog
    Status = models.IntegerField()
    RegistrationStatus = models.IntegerField()
    MarksStatus = models.IntegerField()
    GradeStatus = models.IntegerField()
    class Meta:
        db_table = 'Registration_Status'
        managed = True

    def __str__(self):
        name =  str(DEPARTMENTS[self.Dept-1]) + ':' + str(YEARS[self.BYear]) + ':' + str(SEMS[self.BSem]) + ':' + \
            str(self.AYear) + ':' + str(self.ASem) + ':' + str(self.Regulation) + ':' + str(self.Mode)
        return name

class BranchChanges(models.Model):
    RegNo = models.IntegerField()
    RollNo = models.IntegerField()
    CurrentDept = models.IntegerField()
    NewDept = models.IntegerField()
    AYear = models.IntegerField()
    class Meta:
        db_table = 'BranchChanges'
        managed = True


class HOD(models.Model):
    Faculty = models.ForeignKey('ExamStaffDB.FacultyInfo', on_delete=models.CASCADE)
    Dept = models.IntegerField()
    AssignedDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
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
    Distribution = models.TextField()
    DistributionNames=models.TextField()

    class Meta:
        db_table = 'MarksDistribution'
        unique_together = ('Distribution', 'DistributionNames')
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


class GradePoints(models.Model):
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    Points = models.IntegerField()
    class Meta:
        db_table = 'GradePoints'
        unique_together = ('Regulation', 'Grade', 'Points')
        managed = True