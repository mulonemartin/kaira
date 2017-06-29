""" ``response`` module.
"""
import functools

try:
    from ujson import dumps as json_dumps
except:
    from json import dumps as json_dumps

from .templates import MakoTemplate, template

# see http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
# see http://en.wikipedia.org/wiki/List_of_HTTP_status_codes
HTTP_STATUS = {
    # Informational
    100: '100 Continue',
    101: '101 Switching Protocols',
    # Successful
    200: '200 OK',
    201: '201 Created',
    202: '202 Accepted',
    203: '203 Non-Authoritative Information',
    204: '204 No Content',
    205: '205 Reset Content',
    206: '206 Partial Content',
    207: '207 Multi-Status',
    # Redirection
    300: '300 Multiple Choices',
    301: '301 Moved Permanently',
    302: '302 Found',
    303: '303 See Other',
    304: '304 Not Modified',
    305: '305 Use Proxy',
    307: '307 Temporary Redirect',
    # Client Error
    400: '400 Bad Request',
    401: '401 Unauthorized',
    402: '402 Payment Required',
    403: '403 Forbidden',
    404: '404 Not Found',
    405: '405 Method Not Allowed',
    406: '406 Not Acceptable',
    407: '407 Proxy Authentication Required',
    408: '408 Request Timeout',
    409: '409 Conflict',
    410: '410 Gone',
    411: '411 Length Required',
    412: '412 Precondition Failed',
    413: '413 Request Entity Too Large',
    414: '414 Request-Uri Too Long',
    415: '415 Unsupported Media Type',
    416: '416 Requested Range Not Satisfiable',
    417: '417 Expectation Failed',
    # Server Error
    500: '500 Internal Server Error',
    501: '501 Not Implemented',
    502: '502 Bad Gateway',
    503: '503 Service Unavailable',
    504: '504 Gateway Timeout',
    505: '505 Http Version Not Supported'
}

HTTP_HEADER_CACHE_CONTROL_DEFAULT = ('Cache-Control', 'private')


class BASEHTTPResponse(object):
    status_code = 200
    cache_policy = None
    cache_profile = None


class HTTPResponse(BASEHTTPResponse):
    """ HTTP response """

    def __init__(self,
                 content_type='text/html; charset=UTF-8',
                 encoding='UTF-8',
                 status_code=200):
        """ Initializes HTTP response.
        """

        self.status_code = status_code
        self.content_type = content_type
        self.encoding = encoding
        self.headers = [('Content-Type', content_type)]
        self.buffer = []
        self.cookies = []
        self.cache_dependency = []

    def get_status(self):
        """ Returns a string that describes the specified
            HTTP status code.
        """
        return HTTP_STATUS[self.status_code]

    status = property(get_status)

    def redirect(self, absolute_url, status_code=302):
        """ Redirect response to ``absolute_url`` and sets
            ``status_code``.
        """
        self.status_code = status_code
        self.headers.append(('Location', absolute_url))

    def write(self, chunk):
        """ Applies encoding to ``chunk`` and append it to response
            buffer.
        """
        self.buffer.append(chunk.encode(self.encoding))

    def write_bytes(self, chunk):
        """ Appends chunk it to response buffer. No special checks performed.
            It must be valid object for WSGI response.
        """
        self.buffer.append(chunk)

    def __call__(self, start_response):
        """ WSGI call processing."""
        headers = self.headers
        append = headers.append
        cache_policy = self.cache_policy
        if cache_policy:
            cache_policy.extend(headers)
        else:
            append(HTTP_HEADER_CACHE_CONTROL_DEFAULT)
        if self.cookies:
            encoding = self.encoding
            for cookie in self.cookies:
                append(cookie.http_set_cookie(encoding))
        buffer = self.buffer
        append(('Content-Length', str(sum([len(chunk) for chunk in buffer]))))
        start_response(HTTP_STATUS[self.status_code], headers)
        return buffer


class HandleResponse:

    def __init__(self, template_adapter=MakoTemplate):
        self.render_template = functools.partial(template, template_adapter=template_adapter)

    @staticmethod
    def text(body, status_code=200, cookies=None, encoding="utf-8", headers=None):
        """ text """

        resp = HTTPResponse('text/plain; charset=' + encoding, encoding,
                            status_code=status_code)
        if cookies:
            resp.cookies = cookies
        if headers:
            for header in headers:
                resp.headers.append(header)

        resp.write_bytes(body.encode(encoding))

        return resp

    @staticmethod
    def json(body, status_code=200, cookies=None, encoding="utf-8", headers=None):
        """ json """

        resp = HTTPResponse('application/json; charset=' + encoding, encoding,
                            status_code=status_code)
        if cookies:
            resp.cookies = cookies
        if headers:
            for header in headers:
                resp.headers.append(header)

        resp.write_bytes(json_dumps(body).encode(encoding))

        return resp

    @staticmethod
    def html(body, status_code=200, cookies=None, encoding="utf-8", headers=None):
        """ html """

        resp = HTTPResponse('text/html; charset=' + encoding, encoding,
                            status_code=status_code)
        if cookies:
            resp.cookies = cookies
        if headers:
            for header in headers:
                resp.headers.append(header)

        resp.write_bytes(body.encode(encoding))

        return resp

    @staticmethod
    def redirect(to, status_code=302, encoding="utf-8"):
        """ redirect """

        resp = HTTPResponse('text/html; charset=' + encoding, encoding,
                            status_code=status_code)
        resp.redirect(to, status_code=status_code)

        return resp

    @staticmethod
    def error(body, status_code=400, encoding="utf-8"):
        """ error """

        resp = HTTPResponse('text/html; charset=' + encoding, encoding,
                            status_code=status_code)
        resp.write_bytes(body.encode(encoding))

        return resp

    def template(self, tpl, status_code=200, cookies=None, encoding="utf-8", headers=None, **kwargs):
        """ template """

        body = self.render_template(tpl, **kwargs)

        resp = HTTPResponse('text/html; charset=' + encoding, encoding,
                            status_code=status_code)
        if cookies:
            resp.cookies = cookies
        if headers:
            for header in headers:
                resp.headers.append(header)

        resp.write_bytes(body.encode(encoding))

        return resp

response = HandleResponse()
