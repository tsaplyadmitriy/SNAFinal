# Generated by Django 3.2.6 on 2021-09-14 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0033_auto_20210914_1146'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TestActionCondition',
        ),
        migrations.AddField(
            model_name='test',
            name='name',
            field=models.CharField(default='Тест', max_length=100),
        ),
    ]
