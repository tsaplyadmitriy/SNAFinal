# Generated by Django 3.2.6 on 2021-09-21 17:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0048_alter_course_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='coursecategory',
            options={'verbose_name': 'Категория курсов', 'verbose_name_plural': 'Категории курсов'},
        ),
        migrations.AlterModelOptions(
            name='coursestep',
            options={'ordering': ['step_order']},
        ),
        migrations.AlterModelOptions(
            name='surveyquestion',
            options={'ordering': ['step_order'], 'verbose_name': 'Вопрос опроса', 'verbose_name_plural': 'Вопросы опросов'},
        ),
        migrations.AlterModelOptions(
            name='testevent',
            options={'ordering': ['step_order']},
        ),
        migrations.AlterModelOptions(
            name='testquestion',
            options={'ordering': ['step_order'], 'verbose_name': 'Вопрос к тесту', 'verbose_name_plural': 'Вопросы к тесту'},
        ),
        migrations.AlterModelOptions(
            name='trainingstep',
            options={'ordering': ['step_order'], 'verbose_name': 'Шаг тренировки', 'verbose_name_plural': 'Шаги тренировок'},
        ),
        migrations.AddField(
            model_name='coursestep',
            name='step_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='surveyquestion',
            name='step_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='testevent',
            name='step_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='testquestion',
            name='step_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='trainingstep',
            name='step_order',
            field=models.PositiveIntegerField(default=0),
        ),
    ]