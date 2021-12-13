# Generated by Django 3.2.6 on 2021-09-14 08:37

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0029_auto_20210914_1007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='bot',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.bot'),
        ),
        migrations.CreateModel(
            name='TestEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('threshold', models.IntegerField()),
                ('meaning', models.TextField()),
                ('training', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.training')),
            ],
        ),
    ]
