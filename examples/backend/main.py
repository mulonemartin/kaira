from wtforms import Form, BooleanField, StringField, validators, TextAreaField, PasswordField


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


@app.route("/", methods=['GET'])
def index(request):

    return response.template('index.html')


@app.route("/signin", methods=['GET', 'POST'])
def form_signin(request):

    form = SigninForm(request)
    if form.validate_on_submit():
        return response.redirect('/account')

    return response.template('signin.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def form_register(request):

    form = RegistrationForm(request)
    if form.validate_on_submit():
        return response.redirect('/success')

    return response.template('register.html', form=form)


@app.route("/account")
def account(request):
    return response.text('Welcome to account!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
