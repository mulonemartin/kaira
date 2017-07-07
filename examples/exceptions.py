
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


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
