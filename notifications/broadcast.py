"""
.. _utils:

utility  functions for the notification tasks

:module:    p_soc_auto.notification.utils

:copyright:

    Copyright 2018 Provincial Health Service Authority
    of British Columbia

:contact:    ali.rahmat@phsa.ca

:update:    Oct. 04 2018

"""
import json
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail.message import EmailMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
from ssl_cert_tracker.models import NmapCertsData
from .models import Notification




class Error(Exception):
    """Base class for other exceptions"""
    pass


class InputError(Error):
    """Raised when parameter is not valid"""
    pass


class EmailBroadCast(EmailMessage):
    """
    email broadcast class

    drop in replacement for `djang.core.mail.EmailMessage' that also can
    take a notification obkect and create an email message out of it
    """

    def __init__(
            self, notification_pk=None, subject=None, message=None,
            email_from=settings.ADMINS[0][1], email_to=None, cc=None, bcc=None,
            connection=None, attachments=None,
            reply_to=settings.DEFAULT_EMAIL_REPLY_TO, headers=None,
            email_type=settings.SUB_EMAIL_TYPE, *args, **kwargs):
        """
        :param str subject: email subject
        :param str message: The body of the message
        :param str email_from: email_from
        :param str message: The body of the message
        :param list/tuple email_to: email recepients
        :param list/tuple cc:  email cc
        :param list/tuple bcc: email bcc
        :param obj connection: email connection
        :param list/tuple attachments: email attachments
        :param list/tuple reply_to: email response recepients
        :param dict headers:Extra headers to put on the message
        :param int notification_pk: valid pk if not None.
        :param int email_type: 0:subscribers,
                               1:esc.,
                               2: sub & esc.,
                               otherwise:subscribers
        """
        self.obj = None
        if email_to is None:
            email_to = [address for name, address in settings.ADMINS]

        if notification_pk is None:
            if subject is None or message is None:
                raise InputError("Email Subject/Message")

        try:
            validate_email(email_from)
        except ValidationError:
            raise InputError("Invalid Email From")

        self.validate_email_types(email_to)
        self.validate_email_types(reply_to)
        if attachments is not None:
            self.validate_list_types(attachments)

        # ipdb.set_trace()
        print(notification_pk)
        if Notification.objects.filter(pk=notification_pk).exists():
            self.notification_pk = notification_pk
            self.obj = Notification.objects.get(pk=notification_pk)
            subject, message = self.format_email_subject_message()

            if email_type == settings.SUB_EMAIL_TYPE:
                email_to = self.obj.subscribers
            elif email_type == settings.ESC_EMAIL_TYPE:
                email_to = self.obj.escalation_subscribers
            elif email_type == settings.SUB_ESC_EMAIL_TYPE:
                email_to.extend(
                    self.obj.subscribers).extend(
                    self.obj.escalation)
            else:  # error
                raise InputError('Invalid  data %s', 'email_type')

        super().__init__(subject,
                         message,
                         email_from,
                         email_to,
                         bcc,
                         connection,
                         attachments,
                         cc,
                         reply_to,
                         headers,
                         *args, **kwargs)

    def update_notification_timestamps(self):
        """
        extend this to include the whole send and update logic
        update notification columns upon successful email sent
        days, seconds = duration.days, duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)
        return days, hours, minutes, seconds
        """
        Notification.objects.filter(pk=self.notification_pk).update(
            broadcast_on=timezone.now())
        # we need to update escalated_on if no one paid
        # attension to email within
        # timezone.timedelta(instance.notification_type.escalate_within)

        # Notification.objects.filter(pk=self.notification_pk).update(
        #     escalated_on=timezone.now() +
        #     timezone.timedelta(instance.notification_type.escalate_within))
    def validate_list_types(self, items):
        """
        validates if arguments are list instance
        """
        for item in items:
            if not isinstance(item, (list, tuple)):
                raise InputError(str(item) + ": Not a list instance")

    def validate_email_types(self, email_to):
        """
        validates if argument are email format
        """
        if not isinstance(email_to, (list, tuple)):
            raise InputError(str(email_to) + ": Not a list instance")
        elif len(email_to) == 0:
            raise InputError(str(email_to) + ": Invalid Email")
        else:
            for email in email_to:
                try:
                    validate_email(email)
                except ValidationError:
                    raise InputError(str(email) + ": Invalid Email")
    
    def format_email_subject_message(self):
        ssl_noti = Notification.objects.filter(rule_applies__content_type__model__iexact='nmapcertsdata',instance_pk__in=list(NmapCertsData.objects.values_list('id', flat=True)))[0]
        ssl_cert_obj = ssl_noti.rule_applies.content_type.model_class().objects.get(pk=ssl_noti.instance_pk)
        subject, message_text = display_fields(ssl_cert_obj, self.obj)

        return subject, message_text

def display_fields(cert_instance, noti_instance):
    """
    ssl_cert_display_fields message
    """

    msg_list = []
    noti_rule_msg = json.loads(noti_instance.rule_msg)
    seconds = int(noti_rule_msg["grace_period"]["seconds"])
    day, hous, minutes, sec = convert_seconds_days_hours_minutes(seconds)
    days = int(noti_rule_msg["grace_period"]["days"]) + int(day)

    subject = "Alert = An SSL Cert on <server Name> port 443 will Expire in <#days>"

    host_name = "Place Hoder" # str(cert_instance.name)
    msg_list.append("\nHost Name: " +  host_name)
    msg_list.append("\nNot_valid_before: " + str(cert_instance.not_before))
    msg_list.append("\nNot_valid_after: " +  str(cert_instance.not_after))
    msg_list.append("\n\nIssuer Info")
    msg_list.append("\nOrginization_unit_name: " + "Place Holder")
    msg_list.append("\nOrginization_name: " + cert_instance.organization_name)
    msg_list.append("\nCountry_name: " + cert_instance.country_name)
    msg_list.append("\nCommon_name: " + cert_instance.common_name)
    msg_list.append("\n\nNotification Date: " + noti_rule_msg["now"])
    msg_list.append("\n\nNotification Cause: " + noti_rule_msg["relationship"])
    msg_list.append("\n\nGrace Period:")
    msg_list.append("\n\tDays:" + str(days))
    msg_list.append("\n\tHours:" + str(hous))
    msg_list.append("\n\tMinutes:" + str(minutes))
    msg_list.append("\n\tSeconds:" + str(sec))
    
    message = " ".join(map(str, msg_list))
    return subject, message

def convert_seconds_days_hours_minutes(sec):
    """
    Convert number of seconds into days/hours/min/sec
    """
    dt = datetime(1,1,1) + timedelta(sec)
    return dt.day-1, dt.hour, dt.minute, dt.second

