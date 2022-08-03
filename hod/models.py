from django.db import models

# Create your models here.
from django.contrib.auth import get_user_model
# from ExamStaffDB.models import BTFacultyInfo
User = get_user_model()


class BTFaculty_user(models.Model):
    User= models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey('BTExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE)
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    class Meta:
        db_table = 'BTFaculty_user'
        unique_together=(('User','Faculty','AssignDate','RevokeDate'))
        managed = True


class BTCoordinator(models.Model):
    User= models.ForeignKey(User, on_delete=models.CASCADE)
    Faculty = models.ForeignKey('BTExamStaffDB.BTFacultyInfo', on_delete=models.CASCADE)
    Dept = models.IntegerField()
    BYear = models.IntegerField()
    AssignDate = models.DateTimeField(auto_now_add=True)
    RevokeDate = models.DateTimeField(null=True)
    class Meta:
        db_table = 'BTFaculty_Coordinator'
        unique_together=(('User','Faculty','AssignDate','RevokeDate'))
        managed = True
