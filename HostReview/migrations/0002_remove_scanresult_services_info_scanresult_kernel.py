# Generated by Django 4.2.7 on 2023-11-09 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('HostReview', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scanresult',
            name='services_info',
        ),
        migrations.AddField(
            model_name='scanresult',
            name='kernel',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
