from django import template
from django.contrib.auth.models import Group
from BThod.models import BTFaculty_user
from BTco_ordinator.models import BTFacultyAssignment
from MThod.models import MTFaculty_user
from MTco_ordinator.models import MTFacultyAssignment


register = template.Library()

@register.filter(name = 'BThas_group')
def BThas_group(user, group_name):
    if group_name == 'Course-Co-ordinator':
        faculty = BTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        if faculty:
            courses = BTFacultyAssignment.objects.filter(Coordinator=faculty.Faculty, RegEventId__Status=1).first()
            if courses:
                return True
            return False
        return False
    return user.groups.filter(name=group_name).exists()

@register.filter(name = 'MThas_group')
def MThas_group(user, group_name):
    if group_name == 'Course-Co-ordinator':
        faculty = MTFaculty_user.objects.filter(User=user, RevokeDate__isnull=True).first()
        if faculty:
            courses = MTFacultyAssignment.objects.filter(Coordinator=faculty.Faculty, RegEventId__Status=1).first()
            if courses:
                return True
            return False
        return False
    return user.groups.filter(name=group_name).exists()