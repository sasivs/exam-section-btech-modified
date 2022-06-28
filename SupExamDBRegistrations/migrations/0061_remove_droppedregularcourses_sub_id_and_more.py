# Generated by Django 4.0.4 on 2022-06-27 14:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SupExamDBRegistrations', '0060_alter_droppedregularcourses_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='droppedregularcourses',
            name='sub_id',
        ),
        migrations.AddField(
            model_name='droppedregularcourses',
            name='subject',
            field=models.ForeignKey(default=97, on_delete=django.db.models.deletion.CASCADE, to='SupExamDBRegistrations.subjects'),
        ),
    ]
