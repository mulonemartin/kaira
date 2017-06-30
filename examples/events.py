
from kaira.app import App
from kaira.response import response
from kaira.log import log


app = App()


def handler1_on_request(request):
    """After request"""

    log.info("Handler 1: On request. Request path: %s" % request.path)


def handler2_on_request(request):
    """After request"""

    log.info("Handler 2: On request. Request path: %s" % request.path)


def handler1_on_response(request, response):
    """ on response """

    log.info("Handler 1: On response.")


def handler2_on_response(request, response):
    """ on response """

    log.info("Handler 2: On response.")


@app.route("/",
           on_request=[handler1_on_request, handler2_on_request],
           on_response=[handler1_on_response, handler2_on_response])
def hello_world(request):

    return response.text('Hello World!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
