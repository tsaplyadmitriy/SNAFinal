# Generated by Django 3.2.6 on 2021-09-14 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0034_auto_20210914_1611'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='testevent',
            name='training',
        ),
        migrations.AddField(
            model_name='testevent',
            name='training',
            field=models.ManyToManyField(blank=True, null=True, to='account.Training'),
        ),
    ]
