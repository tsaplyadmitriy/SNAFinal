# Generated by Django 3.2.6 on 2021-08-27 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_test_testresults'),
    ]

    operations = [
        migrations.CreateModel(
            name='Trainer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(max_length=80)),
                ('course', models.ManyToManyField(to='account.Course')),
            ],
        ),
    ]