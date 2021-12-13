# Generated by Django 3.2.6 on 2021-08-27 11:52

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20210827_1420'),
    ]

    operations = [
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('further_actions', models.TextField()),
                ('questions', models.ManyToManyField(to='account.TestQuestion')),
            ],
        ),
        migrations.CreateModel(
            name='TestResults',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result', models.IntegerField(default=0)),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.test')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.client')),
            ],
        ),
    ]
