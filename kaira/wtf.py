from wtforms import Form

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

