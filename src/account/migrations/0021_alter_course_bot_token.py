# Generated by Django 3.2.6 on 2021-09-07 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0020_auto_20210907_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='bot_token',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
