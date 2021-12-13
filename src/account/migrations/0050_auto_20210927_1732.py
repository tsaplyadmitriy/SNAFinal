# Generated by Django 3.2.6 on 2021-09-27 14:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0049_auto_20210921_2021'),
    ]

    operations = [
        migrations.AddField(
            model_name='ticket',
            name='telegram_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='ticket',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.client'),
        ),
    ]