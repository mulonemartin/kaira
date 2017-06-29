import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "../kaira"))


from kaira.app import App
from kaira.response import response
from kaira.wrapper import ContextManager


app = App()


@app.route("/")
def hello_world(request):
    return response.text('Hello World')


@app.route("/json")
def json_hello_world(request):
    return response.json({"msg": "Hello World!"})


class Auth:
    username = ''
    id = 0

    def __init__(self, username="", id_user=0):
        self.username = username
        self.id = id_user


class ContextAuth(ContextManager):

    def on_start(self, request):
        request.auth = Auth(username='Martin', id_user=5)


context_auth = ContextAuth()


@app.route("/context", context=[context_auth])
def context(request):
    return response.text('Hello World! welcome %s' % request.auth.username)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
