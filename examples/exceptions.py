
from kaira.app import App
from kaira.response import response
from kaira.exceptions import http_exception


app = App()


@app.route("/")
def hello_world(request):
    return response.text('Hello World!')


@app.error(404)
def error_404(request):
    return response.text('Error 404', status_code=404)


@app.route("/raise/redirect")
def hello_world_raise(request):
    raise http_exception.redirect('/')


@app.route("/raise/text")
def hello_world_raise_text(request):

    raise http_exception.text('Hellow world', status_code=200)


@app.route("/raise/json")
def hello_world_raise_json(request):
    raise http_exception.json('Hellow world', status_code=200)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
