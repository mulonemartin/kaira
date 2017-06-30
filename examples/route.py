
from kaira.app import App
from kaira.response import response


app = App()


@app.route("/")
def index(request):

    html = '''
    <h1>Index</h1>    
    <ul>
        <li><a href="%(edit)s">Edit</a></li>
        <li><a href="%(post)s">Post</a></li>
        <li><a href="%(translation)s">Translation</a></li>
    </ul>
    ''' % {
        'edit': app.path_for('edit', id=1),
        'post': app.path_for('post', year=2017, month=6),
        'translation': app.path_for('translation', lang='en'),
        }

    return response.html(html)


@app.route("/edit/{id:int}", name='edit')
def edit(request, id):

    return response.text('Hello World! Id: %s' % id)


@app.route("/post/{year:int}/{month:int}", name='post')
def post(request, year, month):

    return response.text('Hello World! year: %s, month: %s' % (year, month))


@app.route("/translation/{lang:(en|ru)}", name='translation')
def translation(request, lang):

    return response.text('Hello World! Locale: %s' % lang)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
