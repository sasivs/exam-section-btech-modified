from django.db.models.signals import post_save
from django.dispatch import receiver
from co_ordinator.models import BTStudentRegistrations, BTSubjects
from faculty.models import Marks, Marks_Staging

@receiver(post_save, sender=BTStudentRegistrations)
def create_marks_instance(sender, instance, created, **kwargs):
    if not Marks.objects.filter(Registration=instance).exists():
        subject = BTSubjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        Marks.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
    if not Marks_Staging.objects.filter(Registration=instance).exists():
        subject = BTSubjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        Marks_Staging.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)

