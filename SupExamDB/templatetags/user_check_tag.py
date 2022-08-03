from django import template
from django.contrib.auth.models import Group
from hod.models import Faculty_user
from co_ordinator.models import BTFacultyAssignment

register = template.Library()

@register.filter(name = 'has_group')
def has_group(user, group_name):
    if group_name == 'Course-Co-ordinator':
        faculty = Faculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        if faculty:
            courses = BTFacultyAssignment.objects.filter(Coordinator=faculty.Faculty, RegEventId__Status=1).first()
            if courses:
                return True
            return False
        return False
    return user.groups.filter(name=group_name).exists()