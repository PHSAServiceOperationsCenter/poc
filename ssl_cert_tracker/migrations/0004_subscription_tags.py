# Generated by Django 2.1.4 on 2019-07-29 20:48

from django.db import migrations, models


class Migration(migrations.Migration):

    # This cannot depend on 0003 because that is being replaced by the data
    # migration. This will cause problems (multiple leaf nodes) for anyone who
    # has either not already
    dependencies = [
        ('ssl_cert_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscription',
            name='tags',
            field=models.TextField(blank=True, help_text='email classification tags placed on the subject line and in the email body', null=True, verbose_name='tags'),
        ),
    ]
