from django.db import models
from BTsuperintendent.models import BTRegistrationStatus, BTGradePoints
from BTco_ordinator.models import BTSubjects, BTStudentRegistrations
# Create your models here.

class BTAttendance_Shortage(models.Model):
    Registration = models.ForeignKey(BTStudentRegistrations, on_delete=models.CASCADE)

    class Meta:
        db_table = 'BTAttendance_Shortage'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_Attendance_shortage_registration')
        ]
        managed = True

class BTGradesThreshold(models.Model):
    Grade = models.ForeignKey(BTGradePoints, on_delete=models.CASCADE)
    Subject = models.ForeignKey(BTSubjects, on_delete=models.CASCADE)
    RegEventId = models.ForeignKey(BTRegistrationStatus, on_delete=models.CASCADE)
    Threshold_Mark = models.IntegerField()
    Section = models.CharField(max_length=2, default='NA')
    class Meta:
        db_table = 'BTGradesThreshold'
        unique_together = (('Grade', 'Subject', 'RegEventId', 'Section'))
        managed = True

class BTMarks_Staging(models.Model):
    Registration = models.ForeignKey(BTStudentRegistrations, on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'BTMarks_Staging'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_Marks_Staging_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = BTSubjects.objects.filter(id=self.Registration.sub_id).first()
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

    def get_marks_list(self):
        marks = self.Marks.split(',')
        marks = [mark.split('+') for mark in marks]
        marks_list = []
        for mark in marks:
            marks_list.extend(mark)
        return marks_list


class BTMarks(models.Model):
    Registration = models.ForeignKey(BTStudentRegistrations, on_delete=models.CASCADE)
    Marks = models.TextField()
    TotalMarks = models.IntegerField()

    class Meta:
        db_table = 'BTMarks'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique_marks_registration')
        ]
        managed = True

    def get_total_marks(self):
        marks_dis = self.Marks.split(',')
        marks_dis = [mark.split('+') for mark in marks_dis]
        subject = BTSubjects.objects.filter(id=self.Registration.sub_id).first()
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


class BTStudentGrades(models.Model):
    RegId= models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'BTStudentGrades'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_StudentGrades_registration')
        ]
        managed = True



class BTStudentGrades_Staging(models.Model):
    RegId = models.IntegerField()
    RegEventId = models.IntegerField()
    Regulation = models.IntegerField()
    Grade = models.CharField(max_length=2)
    AttGrade = models.CharField(max_length=2)
    class Meta:
        db_table = 'BTStudentGrades_Staging'
        constraints = [
            models.UniqueConstraint(fields=['RegId'], name='unique_StudentGrades_Staging_registration')
        ]
        managed = True