# Generated by Django 2.1.1 on 2018-09-18 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssl_cert_tracker', '0002_auto_20180830_2241'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nmapcertsdata',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
        migrations.AlterField(
            model_name='nmapcertsscript',
            name='enabled',
            field=models.BooleanField(db_index=True, default=True, help_text='if this field is checked out, the row will always be excluded from any active operation', verbose_name='enabled'),
        ),
    ]
