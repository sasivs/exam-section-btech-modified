from django.db import models
from ADPGDB.models import MTRegistrationStatus
from MTsuperintendent.models import MTGradePoints
from MTco_ordinator.models import MTSubjects, MTStudentRegistrations
import math
# Create your models here.

class MTAttendance_Shortage(models.Model):
    Registration = models.ForeignKey(MTStudentRegistrations, on_delete=models.CASCADE)

    class Meta:
        db_table = 'MTAttendance_Shortage'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_MTAttendance_shortage_registration')
        ]
        managed = True

class MTGradesThreshold(models.Model):
    Grade = models.ForeignKey(MTGradePoints, on_delete=models.CASCADE)
    Subject = models.ForeignKey(MTSubjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey(MTRegistrationStatus, on_delete=models.CASCADE)
    Threshold_Mark = models.FloatField()
    Exam_Mode = models.BooleanField() 
    class Meta:
        db_table = 'MTGradesThreshold'
        unique_together = (('Grade', 'Subject', 'RegEventId','Exam_Mode'))
        managed = True

class MTMarks_Staging(models.Model):
    Registration = models.ForeignKey(MTStudentRegistrations, on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'MTMarks_Staging'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_MTMarks_Staging_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = MTSubjects.objects.filter(id=self.Registration.sub_id.id).first()
        ratio = subject.DistributionRatio.split(':')
        total_parts = 0
        for part in ratio:
            total_parts += int(part)
        total = 0
        for index in range(len(marks_dis)):
            marks_row = marks_dis[index]
            sub_total = 0
            for mark in marks_row:
                sub_total += float(mark)
            total = sub_total*int(ratio[index])
        return math.ceil(total/total_parts)
    
    def get_marks_list(self):
        marks = self.Marks.split(',')
        marks = [mark.split('+') for mark in marks]
        marks_list = []
        for mark in marks:
            marks_list.extend(mark)
        return marks_list

class MTMarks(models.Model):
    Registration = models.ForeignKey(MTStudentRegistrations, on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'MTMarks'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_MTmarks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = MTSubjects.objects.filter(id=self.Registration.sub_id.id).first()
        ratio = subject.DistributionRatio.split(':')
        total_parts = 0
        for part in ratio:
            total_parts += int(part)
        total = 0
        for index in range(len(marks_dis)):
            marks_row = marks_dis[index]
            sub_total = 0
            for mark in marks_row:
                sub_total += float(mark)
            total = sub_total*int(ratio[index])
        return math.ceil(total/total_parts)

class MTStudentGrades(models.Model):
    RegId = models.IntegerField()
    # AYear = models.IntegerField()
    # ASem = models.IntegerField()
    # SubCode = models.CharField(max_length=10)
    # OfferedYear = models.IntegerField()
    #Dept = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    RegEventId=models.IntegerField()
    class Meta:
        db_table = 'MTStudentGrades'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_MTStudentGrades_registration')
        ]
        managed = True
class MTStudentGrades_Staging(models.Model):
    RegId = models.IntegerField()
    # AYear = models.IntegerField()
    # ASem = models.IntegerField()
    # SubCode = models.CharField(max_length=10)
    # OfferedYear = models.IntegerField()
    # Dept = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    RegEventId=models.IntegerField()
    class Meta:
        db_table = 'MTStudentGrades_Staging'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_MTStudentGrades_Staging_registration')
        ]
        managed = True