from wtforms import Form, BooleanField, StringField, validators, TextAreaField


from kaira.app import App
from kaira.response import response
from kaira.log import log
from kaira.wtf import KairaForm


app = App()


class LoginForm(KairaForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = StringField('Password', [validators.Length(min=6, max=35)])


class RegisterForm(KairaForm):
    name = StringField(u'Full Name', [validators.required(), validators.length(max=10)])
    address = TextAreaField(u'Mailing Address', [validators.optional(), validators.length(max=200)])


class RegistrationForm(KairaForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    accept_rules = BooleanField('I accept the site rules', [validators.InputRequired()])


@app.route("/", methods=['GET', 'POST'])
def form_validation(request):

    form = LoginForm(request)
    if form.validate_on_submit():
        return response.redirect('/good')

    return response.template('forms.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def form_register(request):

    form = RegistrationForm(request)
    if form.validate_on_submit():
        return response.redirect('/good')

    return response.template('register.html', form=form)


@app.route("/good")
def form_good(request):
    return response.text('Good!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
