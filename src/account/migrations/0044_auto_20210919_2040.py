# Generated by Django 3.2.6 on 2021-09-19 17:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0043_alter_ticketmessage_options'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='user_id',
        ),
        migrations.AddField(
            model_name='ticket',
            name='client',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='account.client'),
        ),
    ]
