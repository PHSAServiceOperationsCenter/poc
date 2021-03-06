# Generated by Django 2.2.6 on 2020-01-07 20:13

from django.db import migrations
import re


def replace_serban_with_daniel_in_subscriptions(apps, schema_editor):
    subscription_model = apps.get_model('ssl_cert_tracker', 'Subscription')

    for subscription in subscription_model.objects.all():
        email_list = subscription.emails_list
        if 'daniel.busto' in email_list:
            new_email_list = re.sub('serban\.teodorescu\@phsa\.ca,?', '',
                                    email_list)
        else:
            new_email_list = re.sub('serban\.teodorescu', 'daniel.busto',
                                    email_list)

        subscription.emails_list = new_email_list
        subscription.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ssl_cert_tracker', '0007_merge_20191230_0852'),
    ]

    operations = [
        migrations.RunPython(replace_serban_with_daniel_in_subscriptions)
    ]
