
from kaira.app import App
from kaira.response import response


app = App()


@app.route("/")
def hello_world(request):
    return response.text('Hello World!')


@app.route("/json")
def json_hello_world(request):
    return response.json({"msg": "Hello World!"})


@app.route("/html")
def html_hello_world(request):
    return response.html('<h1>Title</h1>')


@app.route("/redirect")
def redirect_hello_world(request):
    return response.redirect('/html')


@app.route("/page")
def page_hello_world(request):

    try:
        page = request.query['page'][0]
    except:
        page = 0

    return response.text('Hello World! page: %s' % page)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
