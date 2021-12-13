# Generated by Django 3.2.6 on 2021-08-27 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_auto_20210826_1305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accesscode',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='courses_passed',
            field=models.ManyToManyField(blank=True, to='account.Course'),
        ),
        migrations.AlterField(
            model_name='client',
            name='current_step',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.TextField(max_length=12),
        ),
        migrations.AlterField(
            model_name='client',
            name='telegram_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='timezone',
            field=models.TextField(blank=True, max_length=40, null=True),
        ),
    ]
