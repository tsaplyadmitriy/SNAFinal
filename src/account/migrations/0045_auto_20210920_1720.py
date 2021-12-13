# Generated by Django 3.2.6 on 2021-09-20 14:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0044_auto_20210919_2040'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['course_number'], 'verbose_name': 'Курс', 'verbose_name_plural': 'Курсы'},
        ),
        migrations.AddField(
            model_name='course',
            name='course_number',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='CourseCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('courses', models.ManyToManyField(related_name='category', to='account.Course')),
            ],
        ),
    ]
