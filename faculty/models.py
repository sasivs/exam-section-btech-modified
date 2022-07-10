from django.db import models
from SupExamDBRegistrations.models import StudentInfo, RegistrationStatus, Subjects, GradePoints, StudentRegistrations
# Create your models here.

class Attendance_Shortage(models.Model):
    Registration = models.ForeignKey(StudentRegistrations, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Attendance_Shortage'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique registration')
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
            models.UniqueConstraint(fields=['Registration'], name='unique registration')
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
        db_table = 'Marks_Staging'
        constraints = [
            models.UniqueConstraint(fields=['Registration'], name='unique registration')
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