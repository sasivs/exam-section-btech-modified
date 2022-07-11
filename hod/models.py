from django.db import models
from SupExamDBRegistrations.models import FacultyInfo

# Create your models here.
from django.contrib.auth import get_user_model
User = get_user_model()


class FacultyInfo(models.Model):
    FacultyId = models.IntegerField(default=100)
    Name = models.CharField(max_length=100)
    Phone = models.IntegerField()
    Email = models.CharField(max_length=50)
    Dept = models.IntegerField()
    Working = models.BooleanField()
    class Meta:
        db_table = 'FacultyInfo'
        managed = True

class Faculty_user(models.Model):
    User= models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    class Meta:
        db_table = 'Faculty_user'
        unique_together=('User','Faculty','AssignDate','RevokeDate')
        managed = True


class Coordinator(models.Model):
    User= models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey(FacultyInfo, on_delete=models.CASCADE)
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    class Meta:
        db_table = 'Faculty_Coordinator'
        unique_together=('User','Faculty','AssignDate','RevokeDate')
        managed = True
