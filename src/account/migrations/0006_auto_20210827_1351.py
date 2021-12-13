# Generated by Django 3.2.6 on 2021-08-27 10:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_remove_client_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('is_correct', models.BooleanField()),
            ],
        ),
        migrations.AlterField(
            model_name='accesscode',
            name='code',
            field=models.TextField(max_length=16, unique=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='phone',
            field=models.TextField(max_length=12, unique=True),
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('answers', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.answer')),
            ],
        ),
    ]