"""
.. _utils:

utility classes and functions for the p_soc_auto project

:module:    p_soc_auto.p_soc_auto_base.utils

:copyright:

    Copyright 2018 - 2019 Provincial Health Service Authority
    of British Columbia

:contact:    serban.teodorescu@phsa.ca

:update:    Feb. 1, 2019

"""
from django.utils import timezone


def remove_duplicates(sequence=None):
    """
    remove duplicates from a sequence

    :arg sequence: the sequence that may be containing duplicates

    :returns: a ``list`` with no duplicate items
    """
    class IterableError(Exception):
        """
        raise when the input is not, or cannot be cast to, an iterable
        """

        def __init__(self, sequence):
            message = (
                '%s of type %s is not, or cannot be cast to, a sequence' %
                (sequence, type(sequence)))

            super().__init__(message)

    if sequence is None:
        raise IterableError(sequence)

    if not isinstance(sequence, (list, tuple)):
        try:
            sequence = [sequence]
        except Exception:
            raise IterableError(sequence)

    no_dup_sequence = []
    _ = [no_dup_sequence.append(item)
         for item in sequence if item not in no_dup_sequence]

    return no_dup_sequence


def get_pk_list(queryset, pk_field_name='id'):
    """
    get the primary key values from a queryset

    needed when invoking celery tasks without a pickle serializer:

        *    if we pass around model instances, we must use pickle and that
             is a security problem

        *    the proper pattern is to pass around primary keys (usually
             ``int``) which are JSON serializable and pulling the instance
             from the database inside the celery task. note that this will
             increase the number of database access calls considerably

    :arg queryset: the (pre-processed) queryset
    :type queryset: :class"`<django.db.models.query.QuerySet>`

    :arg str pk_field_name:

        the name of the primary key field, (``django``) default 'id'

    :returns: a ``list`` of primary key values
    """
    return list(queryset.values_list(pk_field_name, flat=True))


def _make_aware(datetime_input, use_timezone=timezone.utc, is_dst=False):
    """
    make datetime objects to timezone aware if needed
    """
    if timezone.is_aware(datetime_input):
        return datetime_input

    return timezone.make_aware(
        datetime_input, timezone=use_timezone, is_dst=is_dst)


class RelativeTimeDelta():
    """
    quick and dirty way of calculating a ``datetime.datetime`` object in the
    past relative to another ``datetime.datetime`` object (the reference
    moment).

    in most cases the reference moment is the value returned by
    :method:`<datetime.dateime.now>` but sometimes we need something else
    """
    @staticmethod
    def _now(now):
        """
        static method for the now reference moment
        """
        if now is None:
            now = timezone.now()

        if not isinstance(now, timezone.datetime):
            raise TypeError(
                'Invalid object type %s, was expecting datetime' % type(now))

        return now

    @staticmethod
    def _time_delta(time_delta=None, **kw_time_delta):
        """
        return a proper ``datetime.timedelta`` object. if a dictionary is
        provided instead, try to build the object from the dictionary

        :raises:

            ``exceptions.TypeError`` when :arg:`<time_delta>`` is not of the
            proper type or if the input dictionary cannot be used as argument
            for ``datetime.timedelta``

        :param time_delta: default ``None``
        :type time_delta: ``datetime.timedelta``
        """

        if time_delta is None:
            try:
                time_delta = timezone.timedelta(**kw_time_delta)
            except TypeError as error:
                raise error

        if not isinstance(time_delta, timezone.timedelta):
            raise TypeError(
                'Invalid object type %s, was expecting timedelta'
                % type(time_delta))

        return time_delta

    @classmethod
    def time_delta(cls, time_delta=None, now=None):
        """
        return a relative moment in the past when the interval is specified
        as a ``datetime.timedelta`` object
        """
        if time_delta is None:
            raise TypeError(
                'Invalid object type %s, was expecting timedelta'
                % type(time_delta))

        return RelativeTimeDelta._now(now) \
            - RelativeTimeDelta._time_delta(time_delta)

    @classmethod
    def time_delta_from_dict(cls, now=None, **kw_time_delta):
        """
        return a relative moment in the past when the interval is specified
        as a dictionary suitable for ``datetime.timedelta`` objects
        """
        if not kw_time_delta:
            raise ValueError('you must specify the tiem interval')

        return RelativeTimeDelta._now(now) \
            - RelativeTimeDelta._time_delta(**kw_time_delta)
