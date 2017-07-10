from time import localtime
from time import mktime
import html
import urllib.parse

from datetime import datetime
from datetime import timedelta
from datetime import tzinfo


ZERO = timedelta(0)
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
MONTHS = (
    None, "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")


bytes_type = bytes
str_type = str


def sanitize(text):
    """Gets rid of < and > and & and, for good measure, :"""

    return html.escape(text, quote=True).replace(':', '&#58;')


def n(s, encoding='latin1'):
    if isinstance(s, str_type):
        return s
    return s.decode(encoding)


def format_http_datetime(stamp):
    """ Formats datetime to a string following rfc1123 pattern.

        >>> now = datetime(2011, 9, 19, 10, 45, 30, 0, UTC)
        >>> format_http_datetime(now)
        'Mon, 19 Sep 2011 10:45:30 GMT'

        if timezone is not set in datetime instance the ``stamp``
        is assumed to be in UTC (``datetime.utcnow``).

        >>> now = datetime(2011, 9, 19, 10, 45, 30, 0)
        >>> format_http_datetime(now)
        'Mon, 19 Sep 2011 10:45:30 GMT'

        >>> now = datetime.utcnow()
        >>> assert format_http_datetime(now)

        if ``stamp`` is a string just return it

        >>> format_http_datetime('x')
        'x'

        >>> format_http_datetime(100) # doctest: +ELLIPSIS
        Traceback (most recent call last):
            ...
        TypeError: ...
    """
    if isinstance(stamp, datetime):
        if stamp.tzinfo:
            stamp = stamp.astimezone(UTC).timetuple()
        else:
            stamp = localtime(mktime(stamp.timetuple()))
    elif isinstance(stamp, str):
        return stamp
    else:
        raise TypeError('Expecting type ``datetime.datetime``.')

    year, month, day, hh, mm, ss, wd, y, z = stamp
    return "%s, %02d %3s %4d %02d:%02d:%02d GMT" % (
        WEEKDAYS[wd], day, MONTHS[month], year, hh, mm, ss
    )


class utc(tzinfo):
    """ UTC timezone.

    """
    __slots__ = ('name')

    def __init__(self, name):
        self.name = name

    def tzname(self, dt):
        """ Name of time zone.

            >>> GMT.tzname(None)
            'GMT'
            >>> UTC.tzname(None)
            'UTC'
        """
        return self.name

    def utcoffset(self, dt):
        """ Offset from UTC.

            >>> UTC.utcoffset(None)
            datetime.timedelta(0)
        """
        return ZERO

    def dst(self, dt):
        """ DST is not in effect.

            >>> UTC.dst(None)
            datetime.timedelta(0)
        """
        return ZERO


GMT = utc('GMT')
UTC = utc('UTC')


def url(*args, **kwargs):
    """Url make"""

    func_par = args
    if 'args' in kwargs:
        func_args = kwargs['args']
    else:
        func_args = None

    if 'vars' in kwargs:
        func_vars = kwargs['vars']
    else:
        func_vars = None

    if func_args in (None, []):
        func_args = []

    if not func_par:
        raise SyntaxError("You need to pass at least one argument")

    func_vars = func_vars or {}

    if not isinstance(func_par, (list, tuple)):
        func_par = [func_par]

    if not isinstance(func_args, (list, tuple)):
        func_args = [func_args]

    if func_args:
        other = func_args and urllib.parse.quote(
                '/' + '/'.join([str(x) for x in func_args]))
    else:
        other = ''

    if other.endswith('/'):
        other += '/'    # add trailing slash to make last trailing empty arg explicit

    list_vars = []
    for (key, vals) in sorted(func_vars.items()):
        if not isinstance(vals, (list, tuple)):
            vals = [vals]
        for val in vals:
            list_vars.append((key, val))

    if list_vars:
        other += '?%s' % urllib.parse.urlencode(list_vars)

    func_and_par = func_par and urllib.parse.quote(
        '/' + '/'.join([str(x) for x in func_par]))

    func_and_par = func_and_par.replace('//', '/')

    return func_and_par + other

