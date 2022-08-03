from django.db.models.signals import post_save
from django.dispatch import receiver
from MTco_ordinator.models import MTStudentRegistrations, MTSubjects
from MTfaculty.models import MTMarks, MTMarks_Staging

@receiver(post_save, sender=MTStudentRegistrations)
def create_marks_instance(sender, instance, created, **kwargs):
    if not MTMarks.objects.filter(Registration=instance).exists():
        subject = MTSubjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        MTMarks.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)
    if not MTMarks_Staging.objects.filter(Registration=instance).exists():
        subject = MTSubjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        MTMarks_Staging.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)

