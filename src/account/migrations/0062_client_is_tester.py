# Generated by Django 3.2.6 on 2021-10-08 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0061_auto_20211008_1106'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='is_tester',
            field=models.BooleanField(default=False),
        ),
    ]