import os

from wtforms import TextAreaField, FileField


from kaira.app import App
from kaira.response import response
from kaira.wtf import KairaForm, upload_store


app = App()


class UploadForm(KairaForm):
    image = FileField(u'Image File')
    description = TextAreaField(u'Image Description')


@app.route("/", methods=['GET', 'POST'])
def form_file(request):

    form = UploadForm(request)
    if form.validate_on_submit():
        r_file = request.files['image'][0]
        image_dest = os.path.join('store', 'file.jpg')
        if r_file != '':
            with open(image_dest, 'wb') as jpeg_file:
                upload_store(jpeg_file, r_file)
        return response.redirect('/done')

    return response.template('file.html', form=form)


@app.route("/done")
def done(request):
    return response.text('Done!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
