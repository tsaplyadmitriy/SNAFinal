# Generated by Django 3.2.6 on 2021-09-19 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0041_auto_20210919_1949'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testevent',
            name='training',
            field=models.ManyToManyField(blank=True, to='account.Training'),
        ),
    ]
