
""" ``cookie`` module.
"""

from datetime import datetime
from time import time

from kaira.utils import format_http_datetime, n


class HTTPCookie(object):
    """ HTTP Cookie
        http://www.ietf.org/rfc/rfc2109.txt

        ``domain``, ``secure`` and ``httponly`` are
        taken from ``config`` if not set.
    """
    __slots__ = ('name', 'value', 'path', 'expires',
                 'domain', 'secure', 'httponly')

    def __init__(self, name, value=None, path='/',
                 expires=None, max_age=None,
                 domain=None, secure=None, httponly=None,
                 options=None):
        self.name = name
        self.value = value
        self.path = path
        if max_age is None:
            self.expires = expires
        else:
            self.expires = datetime.utcfromtimestamp(time() + max_age)
        if domain is None:
            self.domain = options['HTTP_COOKIE_DOMAIN']
        else:
            self.domain = domain
        if secure is None:
            self.secure = options['HTTP_COOKIE_SECURE']
        else:
            self.secure = secure
        if httponly is None:
            self.httponly = options['HTTP_COOKIE_HTTPONLY']
        else:
            self.httponly = httponly

    @classmethod
    def delete(cls, name, path='/', domain=None, options=None):
        """ Returns a cookie to be deleted by browser.
        """
        return cls(name,
                   expires='Sat, 01 Jan 2000 00:00:01 GMT',
                   path=path, domain=domain, options=options)

    def http_set_cookie(self, encoding):
        """ Returns Set-Cookie response header.
        """
        directives = []
        append = directives.append
        append(self.name + '=')
        if self.value:
            append(n(self.value, encoding))
        if self.domain:
            append('; domain=' + self.domain)
        if self.expires:
            append('; expires=' + format_http_datetime(self.expires))
        if self.path:
            append('; path=' + self.path)
        if self.secure:
            append('; secure')
        if self.httponly:
            append('; httponly')
        return ('Set-Cookie', ''.join(directives))


class CookieManager(dict):
    """  """

    def __init__(self, options):
        super().__init__()
        self.options = options

    def __setitem__(self, key, value):
        # If this cookie doesn't exist, add it to the header keys
        cookie = HTTPCookie(key, value, options=self.options)
        return super().__setitem__(key, cookie)

    def __delitem__(self, key):

        if key not in self:
            cookie = HTTPCookie(key, '', options=self.options)
            cookie.expires = 'Sat, 01 Jan 2000 00:00:01 GMT'
            #self[key] = cookie
            super().__setitem__(key, cookie)
        else:
            #self[key] = ''
            self[key].expires = 'Sat, 01 Jan 2000 00:00:01 GMT'

