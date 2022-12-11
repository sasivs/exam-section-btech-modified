from django.db import models
from BTco_ordinator.models import BTSubjects
import math
from simple_history.models import HistoricalRecords

# Create your models here.

class BTAttendance_Shortage(models.Model):
    Registration = models.ForeignKey('BTco_ordinator.BTStudentRegistrations', on_delete=models.CASCADE)
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTAttendance_Shortage'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_BTAttendance_shortage_registration')
        ]
        managed = True

class BTGradesThreshold(models.Model):
    Grade = models.ForeignKey('ADAUGDB.BTGradePoints', on_delete=models.CASCADE)
    Subject = models.ForeignKey('BTco_ordinator.BTSubjects', on_delete=models.CASCADE)
    RegEventId = models.ForeignKey('ADAUGDB.BTRegistrationStatus', on_delete=models.CASCADE)
    Threshold_Mark = models.FloatField()
    Section = models.CharField(max_length=2, default='NA')
    Exam_Mode = models.BooleanField() 
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTGradesThreshold'
        unique_together = (('Grade', 'Subject', 'RegEventId', 'Section',"Exam_Mode"))
        managed = True

class BTMarks_Staging(models.Model):
    Registration = models.ForeignKey('BTco_ordinator.BTStudentRegistrations', on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTMarks_Staging'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_BTMarks_Staging_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = BTSubjects.objects.filter(id=self.Registration.sub_id.id).first()
        ratio = subject.course.DistributionRatio.split(':')
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


class BTMarks(models.Model):
    Registration = models.ForeignKey('BTco_ordinator.BTStudentRegistrations', on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()
    history = HistoricalRecords()

    class Meta:
        db_table = 'BTMarks'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_BTmarks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = BTSubjects.objects.filter(id=self.Registration.sub_id.id).first()
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


class BTStudentGrades(models.Model):
    RegId = models.ForeignKey('BTco_ordinator.BTStudentRegistrations',db_column='RegId', on_delete=models.CASCADE)
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTStudentGrades'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_BTStudentGrades_registration')
        ]
        managed = True



class BTStudentGrades_Staging(models.Model):
    RegId = models.ForeignKey('BTco_ordinator.BTStudentRegistrations',db_column='RegId', on_delete=models.CASCADE)
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    history = HistoricalRecords()
    class Meta:
        db_table = 'BTStudentGrades_Staging'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_BTStudentGrades_Staging_registration')
        ]
        managed = True