import base64
import pickle
from datetime import timedelta
import datetime
import hmac
from hashlib import sha1
import os
import hashlib

from wtforms import Form
from wtforms.widgets import HiddenInput
from wtforms.csrf.session import SessionCSRF
from wtforms.csrf.core import CSRF
from wtforms import ValidationError

from multidict import CIMultiDict

from kaira.cookie import CookieManager


SUBMIT_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')


class KairaFormBase(Form):

    def __init__(self, request, **kwargs):

        self.request = request

        self.form_name = 'kaira_form_'
        input_vars = dict()
        if request.method == 'GET':
            input_method = request.query
        elif request.method == 'POST':
            input_method = request.form

        for key, value in input_method.items():
            if isinstance(value, list) and len(value) == 1:
                value = value[0]
            input_vars[key] = value

        input_vars = CIMultiDict(**input_vars)

        super().__init__(formdata=input_vars, **kwargs)
        #self.generate_form_name()  # Generamos el nombre del form (uuid)

    def is_submitted(self):
        """Consider the form submitted if there is an active request and
        the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        """

        return bool(self.request) and self.request.method in SUBMIT_METHODS

    def validate_on_submit(self):
        """Call :meth:`validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return self.is_submitted() and self.validate()

    def hidden_tag(self, *fields):
        """Render the form's hidden fields in one call.
        A field is considered hidden if it uses the
        :class:`~wtforms.widgets.HiddenInput` widget.
        If ``fields`` are given, only render the given fields that
        are hidden.  If a string is passed, render the field with that
        name if it exists.
        .. versionchanged:: 0.13
           No longer wraps inputs in hidden div.
           This is valid HTML 5.
        .. versionchanged:: 0.13
           Skip passed fields that aren't hidden.
           Skip passed names that don't exist.
        """

        def hidden_fields(fields):
            for f in fields:
                if isinstance(f, str):
                    f = getattr(self, f, None)

                if f is None or not isinstance(f.widget, HiddenInput):
                    continue

                yield f

        return u'\n'.join(str(f) for f in hidden_fields(fields or self))

    def generate_form_name(self):
        """Generamos el id"""

        l_fields = list()
        for f in self:
            l_fields.append(f.id)
        sums_ids = ''.join(l_fields)
        hash_code = hashlib.sha256(sums_ids.encode('utf-8')).hexdigest()

        self.form_name = 'kaira_form_' + hash_code

    def render_boostrap_fields(self):
        """ Render fields"""

        xml_form = list()
        for field in self:
            if field.id == 'csrf_token':  # salteamos el csrf token
                continue
            xml_field = list()
            xml_field.append('%s' % field.label)
            xml_field.append('%s' % field(class_='form-control'))
            if field.errors:
                xml_error = list()
                for error in field.errors:
                    xml_error.append('<li>%s</li>' % error)
                xml_field.append('<small class="form-text text-muted">%s</small>' % '\n'.join(xml_error))
            xml_form.append('<div class="form-group">%s</div>' % '\n'.join(xml_field))
        return '\n'.join(xml_form)

    def render_boostrap_form(self, path='/'):
        """ Render form"""

        r_fields = self.render_boostrap_fields()
        submit = '<button type="submit"> Send </button>'
        xml = '<form method="POST" enctype="multipart/form-data" action="{path}">{fields} {submit}</form>'\
            .format(path=path, fields=r_fields, submit=submit)
        return xml


class KSessionCSRF(CSRF):
    TIME_FORMAT = '%Y%m%d%H%M%S'

    def setup_form(self, form):

        self.form_meta = form.meta
        return super(KSessionCSRF, self).setup_form(form)

    def create_session(self):

        meta = self.form_meta
        expire_seconds = int(meta.csrf_options['CSRF_COOKIE_EXPIRE'])
        if expire_seconds > 0:
            now = datetime.datetime.utcnow()
            expires_cookie = now + datetime.timedelta(seconds=expire_seconds)
        else:
            expires_cookie = None

        if not meta.csrf_options['CSRF_COOKIE_DOMAIN'] or meta.csrf_options['CSRF_COOKIE_DOMAIN'] == "":
            domain = meta.request.host.split(':')[0]
        else:
            domain = meta.csrf_options['CSRF_COOKIE_DOMAIN']

        cookies_options = {
            'HTTP_COOKIE_DOMAIN': domain,
            'HTTP_COOKIE_SECURE': meta.csrf_options['CSRF_COOKIE_SECURE'],
            'HTTP_COOKIE_HTTPONLY': meta.csrf_options['CSRF_COOKIE_HTTPONLY']
        }

        cookie_name = meta.csrf_options['CSRF_COOKIE_NAME'] + "_" + meta.form_name
        time_limit = meta.csrf_options['CSRF_TIME_LIMIT']
        csrf_secret = meta.csrf_options['CSRF_SECRET']

        cookies = meta.cookies
        if not cookies:
            cookies = CookieManager(options=cookies_options)

        rand_code = sha1(os.urandom(64)).hexdigest()

        if time_limit:
            expires = (self.now() + time_limit).strftime(self.TIME_FORMAT)
            csrf_build = '%s%s' % (rand_code, expires)
        else:
            expires = ''
            csrf_build = rand_code

        hmac_csrf = hmac.new(csrf_secret, csrf_build.encode('utf8'), digestmod=sha1)
        value_csrf = '%s##%s' % (expires, hmac_csrf.hexdigest())

        cookies[cookie_name] = rand_code
        cookies[cookie_name].path = meta.csrf_options['CSRF_COOKIE_PATH']
        cookies[cookie_name].expires = expires_cookie

        meta.cookies = cookies

        return value_csrf

    def generate_csrf_token(self, csrf_token_field):

        meta = self.form_meta

        request = meta.request
        cookie_name = meta.csrf_options['CSRF_COOKIE_NAME'] + "_" + meta.form_name

        if request.method in ['POST', 'HEAD', 'PUT']:
            if request.cookies:
                if cookie_name in request.cookies:
                    return request.cookies[cookie_name]

        value_csrf = self.create_session()
        return value_csrf

    def delete_session(self):

        meta = self.form_meta
        cookie_name = meta.csrf_options['CSRF_COOKIE_NAME'] + "_" + meta.form_name

        if not meta.csrf_options['CSRF_COOKIE_DOMAIN'] or meta.csrf_options['CSRF_COOKIE_DOMAIN'] == "":
            domain = meta.request.host.split(':')[0]
        else:
            domain = meta.csrf_options['CSRF_COOKIE_DOMAIN']

        cookies_options = {
            'HTTP_COOKIE_DOMAIN': domain,
            'HTTP_COOKIE_SECURE': meta.csrf_options['CSRF_COOKIE_SECURE'],
            'HTTP_COOKIE_HTTPONLY': meta.csrf_options['CSRF_COOKIE_HTTPONLY']
        }

        cookies = meta.cookies
        if not cookies:
            cookies = CookieManager(options=cookies_options)

        del cookies[cookie_name]

        meta.cookies = cookies

    def validate_csrf_token(self, form, field):

        meta = self.form_meta

        time_limit = meta.csrf_options['CSRF_TIME_LIMIT']
        csrf_secret = meta.csrf_options['CSRF_SECRET']
        cookie_name = meta.csrf_options['CSRF_COOKIE_NAME'] + "_" + meta.form_name
        request = meta.request

        if not field.data or '##' not in field.data:
            raise ValidationError(field.gettext('CSRF token missing'))

        expires, hmac_csrf = field.data.split('##', 1)

        check_val = (str(request.cookies[cookie_name]) + expires).encode('utf8')

        hmac_compare = hmac.new(csrf_secret, check_val, digestmod=sha1)
        if hmac_compare.hexdigest() != hmac_csrf:
            raise ValidationError(field.gettext('CSRF failed'))

        if time_limit:
            now_formatted = self.now().strftime(self.TIME_FORMAT)
            if now_formatted > expires:
                raise ValidationError(field.gettext('CSRF token expired'))

    def now(self):
        """
        Get the current time. Used for test mocking/overriding mainly.
        """
        return datetime.datetime.now()


class KairaForm(KairaFormBase):

    class Meta:
        csrf = True
        csrf_class = KSessionCSRF
        csrf_options = {
            'CSRF_COOKIE_DOMAIN': '',
            'CSRF_COOKIE_SECURE': False,
            'CSRF_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_EXPIRE': 3600,
            'CSRF_COOKIE_PATH': '/',
            'CSRF_COOKIE_NAME': 'csrf',
            'CSRF_SECRET': b'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
            'CSRF_TIME_LIMIT': timedelta(minutes=60)
            }

    def __init__(self, request, cookies=None, csrf_options=None, form_name='my_form', **kwargs):

        self.request = request
        self.csrf_options = csrf_options
        self.cookies = cookies
        if not csrf_options:
            csrf_options = {
                'CSRF_COOKIE_DOMAIN': '',
                'CSRF_COOKIE_SECURE': False,
                'CSRF_COOKIE_HTTPONLY': True,
                'CSRF_COOKIE_EXPIRE': 3600,
                'CSRF_COOKIE_PATH': '/',
                'CSRF_COOKIE_NAME': 'csrf',
                'CSRF_SECRET': b'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
                'CSRF_TIME_LIMIT': timedelta(minutes=60)
            }

        super().__init__(request=request, meta=dict(cookies=cookies,
                                                    request=request,
                                                    csrf_options=csrf_options,
                                                    form_name=form_name), **kwargs)

    def render_boostrap_form(self, path='/', send_caption='Send'):
        """ Render form"""

        r_fields = self.render_boostrap_fields()
        if self.csrf_token.errors:
            csrf_errors = self.csrf_token.errors
        else:
            csrf_errors = ''
        submit = '<button type="submit"> {send_caption} </button>'.format(send_caption=send_caption)
        xml = '<form method="POST" enctype="multipart/form-data" action="{path}">' \
              '{csrf_token} {csrf_errors}' \
              '{fields} ' \
              '{submit}' \
              '</form>'\
            .format(path=path,
                    fields=r_fields,
                    submit=submit,
                    csrf_token=self.csrf_token,
                    csrf_errors=csrf_errors)
        return xml


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


def upload_store(file_dest, upload_file):
    """Store the file"""

    upload_file.file.seek(0)
    for piece in read_in_chunks(upload_file.file):
        file_dest.write(piece)

    return file_dest


def serialize(obj):
    return base64.b64encode(pickle.dumps(obj))


def deserialize(s):
    return pickle.loads(base64.b64decode(s))

