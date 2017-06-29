import os

from kaira.app import App
from kaira.response import response


app = App()
app.static('/static/', os.path.join(os.path.dirname(__file__), "static"))


@app.route("/")
def hello_world(request):
    return response.html('<h1>Hello World!</h1> <p><img src="/static/photo2.png" width="400" height="300" /></p>')


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000)
