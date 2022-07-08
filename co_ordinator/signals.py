from django.db.models.signals import post_save
from django.dispatch import receiver
from SupExamDBRegistrations.models import StudentRegistrations, Subjects
from faculty.models import Marks

@receiver(post_save, sender=StudentRegistrations)
def create_marks_instance(sender, instance, created, **kwargs):
    if not Marks.objects.filter(Registration=instance).exists():
        subject = Subjects.objects.get(id=instance.sub_id)
        mark_distribution = subject.MarkDistribution
        Marks.objects.create(Registration=instance, Marks=mark_distribution.get_zeroes_string(), TotalMarks=0)

