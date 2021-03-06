# Generated by Django 3.2.6 on 2021-09-14 04:53

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0024_bot_current_port'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='testquestion',
            options={'ordering': ['id'], 'verbose_name': 'Вопрос к тесту', 'verbose_name_plural': 'Вопросы к тесту'},
        ),
        migrations.AddField(
            model_name='client',
            name='current_course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_course', to='account.course'),
        ),
        migrations.AlterField(
            model_name='bot',
            name='current_port',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='courses_passed',
            field=models.ManyToManyField(blank=True, related_name='courses_passed', to='account.Course'),
        ),
    ]
