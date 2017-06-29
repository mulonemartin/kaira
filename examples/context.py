
from kaira.app import App
from kaira.response import response
from kaira.wrapper import ContextManager
from kaira.log import log


app = App()


class ContextHandler(ContextManager):
    def __init__(self, name="default"):
        self.name = name

    def on_start(self, request):
        log.info("On start: '%s'" % self.name)

    def on_success(self, request):
        log.info("On success: '%s'" % self.name)

    def on_failure(self, request):
        log.info("On fail: '%s'" % self.name)


context_1 = ContextHandler('context 1')
context_2 = ContextHandler('context 2')


@app.route("/", context=[context_1, context_2])
def hello_world(request):
    return response.text('Hello World!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
