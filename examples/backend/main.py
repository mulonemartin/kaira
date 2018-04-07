from wtforms import Form, BooleanField, StringField, validators, \
    TextAreaField, PasswordField, SelectField, SelectMultipleField, \
    IntegerField, FormField, RadioField, DateField


from kaira.app import App
from kaira.response import response
from kaira.log import log
from kaira.wtf import KairaForm


app = App()


class SigninForm(KairaForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = StringField('Password', [validators.Length(min=6, max=35)])


class RegistrationForm(KairaForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])


class TestForm(KairaForm):
    language = SelectField(u'Programming Language', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    multiple = SelectMultipleField(u'cpp', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    radio = RadioField(u'One', choices=[('cpp', 'C++'), ('py', 'Python'), ('text', 'Plain Text')])
    accept_tos = BooleanField('I accept the TOS', [validators.DataRequired()])
    date = DateField(u'Date', format='%Y-%m-%d')


class TelephoneForm(KairaForm):
    country_code = IntegerField('Country Code', [validators.required()])
    area_code = IntegerField('Area Code/Exchange', [validators.required()])
    number = StringField('Number')


class ContactForm(KairaForm):
    first_name = StringField()
    last_name = StringField()
    mobile_phone = FormField(TelephoneForm)
    office_phone = FormField(TelephoneForm)


@app.route("/", methods=['GET'])
def index(request):

    return response.template('index.html')


@app.route("/signin", methods=['GET', 'POST'])
def form_signin(request):

    form = SigninForm(request)
    if form.validate_on_submit():
        return response.redirect('/account')

    return response.template('signin.html', form=form)


@app.route("/test", methods=['GET', 'POST'])
def form_test(request):

    form = TestForm(request)
    if form.validate_on_submit():
        return response.redirect('/account')

    return response.template('test.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def form_register(request):

    form = RegistrationForm(request)
    if form.validate_on_submit():
        print(form.username.data)
        return response.redirect('/success')

    return response.template('register.html', form=form)


@app.route("/account")
def account(request):
    return response.text('Welcome to account!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
