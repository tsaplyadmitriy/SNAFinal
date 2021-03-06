# Generated by Django 3.2.6 on 2021-09-18 08:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0038_client_handle'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('image', models.ImageField(upload_to='')),
            ],
            options={
                'verbose_name': 'Информационное сообщение',
                'verbose_name_plural': 'Информационные сообщения',
            },
        ),
        migrations.RemoveField(
            model_name='coursestep',
            name='text',
        ),
        migrations.AlterField(
            model_name='client',
            name='courses_passed',
            field=models.ManyToManyField(blank=True, related_name='courses_passed', to='account.Course', verbose_name='Пройденные курсы'),
        ),
        migrations.AlterField(
            model_name='client',
            name='telegram_id',
            field=models.IntegerField(blank=True, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='coursestep',
            name='text_message',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_steps', to='account.textmessage'),
        ),
    ]
