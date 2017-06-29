""" Request module"""

import sys
from cgi import FieldStorage
import json
from urllib.parse import urlunsplit
from urllib.parse import unquote

try:
    from ujson import loads as json_loads
except ImportError:
    if sys.version_info[:2] == (3, 5):
        def json_loads(data):
            # on Python 3.5 json.loads only supports str not bytes
            return json.loads(data.decode())
    else:
        json_loads = json.loads

try:  # pragma: nocover
    # Python 2.5+
    partition = str.partition
except AttributeError:  # pragma: nocover
    def partition(s, sep):
        if sep in s:
            a, b = s.split(sep, 1)
            return a, sep, b
        else:
            return s, sep, ''


MULTIPART_ENVIRON = {'REQUEST_METHOD': 'POST'}


class attribute(object):
    """ ``attribute`` decorator is intended to promote a
        function call to object attribute. This means the
        function is called once and replaced with
        returned value.

        >>> class A:
        ...     def __init__(self):
        ...         self.counter = 0
        ...     @attribute
        ...     def count(self):
        ...         self.counter += 1
        ...         return self.counter
        >>> a = A()
        >>> a.count
        1
        >>> a.count
        1
    """
    __slots__ = ('f')

    def __init__(self, f):
        self.f = f

    def __get__(self, obj, t=None):
        f = self.f
        val = f(obj)
        setattr(obj, f.__name__, val)
        return val


class HTTPRequest(object):
    """  """

    app = None
    auth = None

    def __init__(self, environ: dict, encoding: str, max_content_lenght: int=4*1024*1024) -> None:
        self.environ = environ
        self.encoding = encoding
        self.max_content_lenght = max_content_lenght
        self.method = environ['REQUEST_METHOD']

    @attribute
    def host(self) -> str:
        host = self.environ['HTTP_HOST']
        if ',' in host:
            host = host.rsplit(',', 1)[-1].strip()
        return host

    @attribute
    def remote_addr(self) -> str:
        addr = self.environ['REMOTE_ADDR']
        if ',' in addr:
            addr = addr.split(',', 1)[0].strip()
        return addr

    @attribute
    def root_path(self) -> str:
        return self.environ['SCRIPT_NAME'] + '/'

    @attribute
    def path(self) -> str:
        return self.environ['SCRIPT_NAME'] + self.environ['PATH_INFO']

    @attribute
    def query(self) -> str:
        return parse_qs(self.environ['QUERY_STRING'])

    def get_param(self, name):
        p = self.query.get(name)
        return p and p[-1]

    @attribute
    def form(self):
        form, self.files = self.load_body()
        return form

    @attribute
    def files(self):
        self.form, files = self.load_body()
        return files

    @attribute
    def json(self):
        json_b, self.files = self.load_body()
        return json_b

    @attribute
    def cookies(self):
        if 'HTTP_COOKIE' in self.environ:
            return parse_cookie(self.environ['HTTP_COOKIE'])
        else:
            return {}

    @attribute
    def ajax(self):
        if 'HTTP_X_REQUESTED_WITH' in self.environ:
            return self.environ['HTTP_X_REQUESTED_WITH'] == 'XMLHttpRequest'
        else:
            return False

    @attribute
    def secure(self) -> bool:
        return self.environ['wsgi.url_scheme'] == 'https'

    @attribute
    def scheme(self) -> str:
        return self.environ['wsgi.url_scheme']

    @attribute
    def urlparts(self):
        return UrlParts((self.scheme, self.host,
                         self.path, self.environ['QUERY_STRING'], None))

    @attribute
    def content_type(self) -> str:
        return self.environ['CONTENT_TYPE']

    @attribute
    def content_length(self) -> int:
        return int(self.environ['CONTENT_LENGTH'])

    @attribute
    def stream(self):
        return self.environ['wsgi.input']

    def load_body(self):
        """ Load http request body and returns
            form data and files.
        """
        environ = self.environ
        cl = environ['CONTENT_LENGTH']
        icl = int(cl)
        if icl > self.max_content_lenght:
            raise ValueError('Maximum content length exceeded')
        fp = environ['wsgi.input']
        ct = environ['CONTENT_TYPE']
        # application/x-www-form-urlencoded
        if '/x' in ct:
            return parse_qs(fp.read(icl).decode(self.encoding)), None
        # application/json
        elif '/j' in ct:
            return json_loads(fp.read(icl).decode(self.encoding)), None
        # multipart/form-data
        elif ct.startswith('m'):
            return parse_multipart(fp, ct, cl, self.encoding)
        else:
            return None, None


def parse_qs(qs):
    params = {}
    for field in qs.split('&'):
        r = partition(field, '=')
        k = r[0]
        v = r[2]
        if '+' in k:
            k = k.replace('+', ' ')
        if '%' in k:
            k = unquote(k)
        if '+' in v:
            v = v.replace('+', ' ')
        if k in params:
            params[k].append('%' in v and unquote(v) or v)
        else:
            if ',' in v:
                params[k] = [('%' in v and unquote(x) or x)
                             for x in v.split(',')]
            else:
                params[k] = ['%' in v and unquote(v) or v]
    return params


def parse_multipart(fp, ctype, clength, encoding):
    """ Parse multipart/form-data request. Returns
        a tuple (form, files).
    """
    fs = FieldStorage(
        fp=fp,
        environ=MULTIPART_ENVIRON,
        headers={
            'content-type': ctype,
            'content-length': clength
        },
        keep_blank_values=True
    )
    form = {}
    files = {}
    for f in fs.list:
        if f.filename:
            files.setdefault(f.name, []).append(f)
        else:
            form.setdefault(f.name, []).append(f.value)
    return form, files


def parse_cookie(cookie):
    """ Parse cookie string and return a dictionary
        where key is a name of the cookie and value
        is cookie value.
    """
    return cookie and dict([pair.split('=', 1)
                            for pair in cookie.split('; ')]) or {}


def urlparts(parts=None, scheme=None, netloc=None, path=None,
             query=None, fragment=None):
    """  """
    if not parts:
        parts = (scheme, netloc, path, query, fragment)
    return UrlParts(parts)


class UrlParts(tuple):
    """ Concrete class for :func:`urlparse.urlsplit` results.
    """

    def __init__(self, parts):
        assert len(parts) == 5, '`parts` must be a tupple of length 6'
        super(UrlParts, self).__init__()

    def __repr__(self):
        return 'urlparts' + super(UrlParts, self).__repr__()

    def geturl(self):
        """ """
        return urlunsplit(self)

    def join(self, other):
        """  """
        parts = (
            other[0] or self[0],
            other[1] or self[1],
            other[2] or self[2],
            other[3],
            other[4])
        return UrlParts(parts)
