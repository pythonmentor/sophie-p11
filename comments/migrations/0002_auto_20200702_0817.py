# Generated by Django 3.0.7 on 2020-07-02 06:17

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commentsdb',
            name='date',
            field=models.DateTimeField(verbose_name=django.utils.timezone.now),
        ),
    ]
