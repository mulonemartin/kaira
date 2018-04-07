import base64
import pickle

from wtforms import Form
from wtforms.widgets import HiddenInput

from multidict import CIMultiDict


SUBMIT_METHODS = ('POST', 'PUT', 'PATCH', 'DELETE')


class KairaForm(Form):

    def __init__(self, request, **kwargs):

        self.request = request

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

    def render_boostrap_fields(self):
        """ Render fields"""

        xml_form = list()
        for field in self:
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
