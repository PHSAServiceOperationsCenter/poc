# Generated by Django 2.1.1 on 2018-12-12 23:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ssl_cert_tracker', '0013_merge_20181205_1559'),
    ]

    operations = [
        migrations.AlterField(
            model_name='historicalnmapcertsdata',
            name='not_after',
            field=models.DateTimeField(db_index=True, help_text='certificate not valid after this date', verbose_name='expires in'),
        ),
        migrations.AlterField(
            model_name='nmapcertsdata',
            name='not_after',
            field=models.DateTimeField(db_index=True, help_text='certificate not valid after this date', verbose_name='expires in'),
        ),
    ]
