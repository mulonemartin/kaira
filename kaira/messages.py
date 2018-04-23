""" Messages module """

from datetime import timedelta
import datetime

# Kaira import
from kaira.signing import dumps as signing_dumps
from kaira.signing import loads as signing_loads
from kaira.cookie import CookieManager
from kaira.wrapper import ContextManager


DEBUG = 10
INFO = 20
SUCCESS = 25
WARNING = 30
ERROR = 40

DEFAULT_TAGS = {
    DEBUG: 'debug',
    INFO: 'info',
    SUCCESS: 'success',
    WARNING: 'warning',
    ERROR: 'error',
}

DEFAULT_LEVELS = {
    'DEBUG': DEBUG,
    'INFO': INFO,
    'SUCCESS': SUCCESS,
    'WARNING': WARNING,
    'ERROR': ERROR,
}
"""
messages = [{'msg': 'hola mundo', 'lvl': 20}, {'msg': 'hola mundo 2', 'lvl': 20}]
"""


class MessagesManager:

    # uwsgi's default configuration enforces a maximum size of 4kb for all the
    # HTTP headers. In order to leave some room for other cookies and headers,
    # restrict the session cookie to 1/2 of 4kb. See #18781.
    max_cookie_size = 2048
    request = None
    cookies = None
    _queued_messages = []
    used = False
    messages = []
    response_cookies = None

    def __init__(self, options=None):

        if not options:
            options = {
                       'MESSAGES_COOKIE_DOMAIN': '',
                       'MESSAGES_COOKIE_SECURE': False,
                       'MESSAGES_COOKIE_HTTPONLY': True,
                       'MESSAGES_COOKIE_EXPIRE': 600,
                       'MESSAGES_COOKIE_PATH': '/',
                       'MESSAGES_COOKIE_NAME': 'kaira_message',
                       'MESSAGES_SECRET': b'APj00cpfa8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
                       'MESSAGES_TIME_LIMIT': timedelta(minutes=60)
                      }
        self.options = options

    def start(self, request, cookies=None):
        self.request = request
        self.cookies = cookies
        self._queued_messages = []
        self.used = False
        self.messages = []
        self.response_cookies = None
        self.load()  # load messages from cookies

    def load(self):
        """ Get messages from cookie """
        cookie_name = self.options['MESSAGES_COOKIE_NAME']
        try:
            data = self.request.cookies[cookie_name]
        except KeyError:
            data = None

        messages = None
        if data:
            messages = self._decode(data)

        if self.used:
            self.delete_cookie()

        self.messages = messages

        return messages

    def add_message(self, msg, msg_level=INFO):
        self._queued_messages.append(dict(msg=msg, lvl=msg_level))
        self.store_cookie()

    def info(self, msg):
        self.add_message(msg, msg_level=INFO)

    def debug(self, msg):
        self.add_message(msg, msg_level=DEBUG)

    def warning(self, msg):
        self.add_message(msg, msg_level=WARNING)

    def error(self, msg):
        self.add_message(msg, msg_level=ERROR)

    def success(self, msg):
        self.add_message(msg, msg_level=SUCCESS)

    def store_cookie(self):

        encoded_data = self._encode(self._queued_messages)

        expire_seconds = int(self.options['MESSAGES_COOKIE_EXPIRE'])
        if expire_seconds > 0:
            now = datetime.datetime.utcnow()
            expires_cookie = now + datetime.timedelta(seconds=expire_seconds)
        else:
            expires_cookie = None

        if not self.options['MESSAGES_COOKIE_DOMAIN'] or self.options['MESSAGES_COOKIE_DOMAIN'] == "":
            domain = self.request.host.split(':')[0]
        else:
            domain = self.options['MESSAGES_COOKIE_DOMAIN']

        cookies_options = {
            'HTTP_COOKIE_DOMAIN': domain,
            'HTTP_COOKIE_SECURE': self.options['MESSAGES_COOKIE_SECURE'],
            'HTTP_COOKIE_HTTPONLY': self.options['MESSAGES_COOKIE_HTTPONLY']
        }

        cookie_name = self.options['MESSAGES_COOKIE_NAME']

        cookies = self.cookies
        if not cookies:
            cookies = CookieManager(options=cookies_options)

        cookies[cookie_name] = encoded_data
        cookies[cookie_name].path = self.options['MESSAGES_COOKIE_PATH']
        cookies[cookie_name].expires = expires_cookie

        self.response_cookies = cookies

    def delete_cookie(self):

        cookie_name = self.options['MESSAGES_COOKIE_NAME']

        if not self.options['MESSAGES_COOKIE_DOMAIN'] or self.options['MESSAGES_COOKIE_DOMAIN'] == "":
            domain = self.request.host.split(':')[0]
        else:
            domain = self.options['MESSAGES_COOKIE_DOMAIN']

        cookies_options = {
            'HTTP_COOKIE_DOMAIN': domain,
            'HTTP_COOKIE_SECURE': self.options['MESSAGES_COOKIE_SECURE'],
            'HTTP_COOKIE_HTTPONLY': self.options['MESSAGES_COOKIE_HTTPONLY']
        }

        cookies = self.cookies
        if not cookies:
            cookies = CookieManager(options=cookies_options)

        del cookies[cookie_name]

        self.response_cookies = cookies

    def _encode(self, messages, encode_empty=False):

        if messages or encode_empty:
            value = signing_dumps(messages,
                                  key=self.options['MESSAGES_SECRET'])
            return value

    def _decode(self, data):

        if not data:
            return None

        try:
            messages = signing_loads(data,
                                     key=self.options['MESSAGES_SECRET'],
                                     max_age=self.options['MESSAGES_TIME_LIMIT'])
            self.used = True
        except:
            messages = None
            self.used = True

        return messages

    def render(self):

        xml_messages = list()
        if self.messages:
            for message in self.messages:

                xml = '''
                      <div class="alert alert-%(render_class)s">
                      <button type="button" class="close" data-dismiss="alert">&times;</button>
                      %(message)s
                      </div>
                      ''' % {'render_class': DEFAULT_TAGS[message['lvl']],
                             'message': message['msg']}
                xml_messages.append(xml)

            return '\n'.join(xml_messages)
        return ''


class ContextMessages(ContextManager):
    messages_manager = None

    def __init__(self, options=None):
        self.options = options
        messages_manager = MessagesManager(options)
        self.messages_manager = messages_manager

    def on_start(self, request):
        self.messages_manager.start(request)

    def add_message(self, msg, lvl=INFO):
        self.messages_manager.add_message(msg, lvl)

    def info(self, msg):
        self.messages_manager.add_message(msg, msg_level=INFO)

    def debug(self, msg):
        self.messages_manager.add_message(msg, msg_level=DEBUG)

    def warning(self, msg):
        self.messages_manager.add_message(msg, msg_level=WARNING)

    def error(self, msg):
        self.messages_manager.add_message(msg, msg_level=ERROR)

    def success(self, msg):
        self.messages_manager.add_message(msg, msg_level=SUCCESS)

    def render(self):
        return self.messages_manager.render()

    @property
    def response_cookies(self):
        return self.messages_manager.response_cookies
