from wtforms import StringField, validators


from kaira.app import App
from kaira.response import response
from kaira.wtf import KairaForm


app = App()


class SigninForm(KairaForm):
    username = StringField('Username', [validators.Length(min=4, max=25)])
    password = StringField('Password', [validators.Length(min=6, max=35)])


@app.route("/", methods=['GET', 'POST'])
def form_boostrap(request):

    form = SigninForm(request)
    if form.validate_on_submit():
        return response.redirect('/done')

    return response.template('boostrap.html', form=form)


@app.route("/done")
def done(request):
    return response.text('Done!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
