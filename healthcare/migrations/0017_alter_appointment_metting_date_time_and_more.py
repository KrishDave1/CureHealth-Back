# Generated by Django 4.2.6 on 2023-10-29 11:07

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthcare', '0016_alter_appointment_metting_date_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='metting_Date_Time',
            field=models.DateTimeField(default=datetime.datetime(2023, 10, 29, 5, 37, 6, 675575, tzinfo=datetime.timezone.utc), verbose_name='Meeting Date and Time'),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='healthcare.patient'),
        ),
    ]
