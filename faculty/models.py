from django.db import models
from superintendent.models import RegistrationStatus, GradePoints
from co_ordinator.models import Subjects, StudentRegistrations
# Create your models here.

class Attendance_Shortage(models.Model):
    Registration = models.ForeignKey(StudentRegistrations, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Attendance_Shortage'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_Attendance_shortage_registration')
        ]
        managed = True

class GradesThreshold(models.Model):
    Grade = models.ForeignKey(GradePoints, on_delete=models.CASCADE)
    Subject = models.ForeignKey(Subjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey(RegistrationStatus, on_delete=models.CASCADE)
    Threshold_Mark = models.IntegerField()
    uniform_grading = models.BooleanField()
    Section = models.CharField(max_length=2, default='NA')
    class Meta:
        db_table = 'GradesThreshold'
        unique_together = ('Grade', 'Subject', 'RegEventId', 'Section')
        managed = True

class Marks_Staging(models.Model):
    Registration = models.ForeignKey(StudentRegistrations, on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'Marks_Staging'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_Marks_Staging_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = Subjects.objects.filter(id=self.Registration.sub_id).first()
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

class Marks(models.Model):
    Registration = models.ForeignKey(StudentRegistrations, on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'Marks'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_marks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = Subjects.objects.filter(id=self.Registration.sub_id).first()
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


class StudentGrades(models.Model):
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'StudentGrades'
        managed = True



class StudentGrades_Staging(models.Model):
    RegId = models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'StudentGrades_Staging'
        managed = True