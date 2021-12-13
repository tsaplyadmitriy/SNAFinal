# Generated by Django 3.2.6 on 2021-10-08 07:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0058_auto_20211006_1832'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('header', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='')),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
            ],
            options={
                'verbose_name': 'Текстовое сообщение',
            },
        ),
        migrations.RemoveField(
            model_name='coursestep',
            name='text_message',
        ),
        migrations.RemoveField(
            model_name='coursestep',
            name='text_message_file',
        ),
        migrations.RemoveField(
            model_name='coursestep',
            name='text_message_image',
        ),
        migrations.AddField(
            model_name='client',
            name='previous_step',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coursestep',
            name='text',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='course_steps', to='account.textmessage'),
        ),
    ]