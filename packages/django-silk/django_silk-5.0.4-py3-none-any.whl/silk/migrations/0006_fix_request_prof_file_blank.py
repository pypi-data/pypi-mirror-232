# Generated by Django 2.0 on 2017-12-28 14:21

from django.db import migrations, models

import silk.storage


class Migration(migrations.Migration):

    dependencies = [
        ('silk', '0005_increase_request_prof_file_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='prof_file',
            field=models.FileField(blank=True, max_length=300, storage=silk.storage.ProfilerResultStorage(), upload_to=''),
        ),
    ]
