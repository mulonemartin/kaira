from wtforms import Form, BooleanField, StringField, validators


from kaira.app import App
from kaira.response import response
from kaira.log import log
from kaira.wtf import KairaForm


app = App()


class LoginForm(KairaForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = StringField('Password', [validators.Length(min=6, max=35)])


@app.route("/", methods=['GET', 'POST'])
def form_validation(request):

    form = LoginForm(request)
    if form.validate_on_submit():
        return response.redirect('/good')

    return response.template('forms.html', form=form)


@app.route("/good")
def form_good(request):
    return response.text('Good!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
