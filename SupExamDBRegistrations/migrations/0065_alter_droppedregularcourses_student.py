# Generated by Django 4.0.4 on 2022-06-27 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('SupExamDBRegistrations', '0064_remove_droppedregularcourses_regno_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='droppedregularcourses',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='SupExamDBRegistrations.studentinfo'),
        ),
    ]
