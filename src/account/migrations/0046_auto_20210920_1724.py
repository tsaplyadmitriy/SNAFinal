# Generated by Django 3.2.6 on 2021-09-20 14:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0045_auto_20210920_1720'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accesscode',
            name='course',
        ),
        migrations.AddField(
            model_name='accesscode',
            name='course_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='account.coursecategory'),
        ),
    ]
