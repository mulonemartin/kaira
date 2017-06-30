
from kaira.app import App
from kaira.response import response


app = App()


@app.route("/")
def hello_world(request):
    tpl = 'Hello ${name}'
    return response.template(tpl, name='World')


@app.route("/view")
def view_hello_world(request):
    return response.template('index.html', myname='Martin')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
