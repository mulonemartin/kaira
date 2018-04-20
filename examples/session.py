
from kaira.app import App
from kaira.response import response


app = App()


@app.route("/")
def hello_world(request):
    return response.text('Hello World!')