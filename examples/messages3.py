
from kaira.app import App
from kaira.response import ContextResponse
from kaira.exceptions import http_exception


app = App()


ctx_response = ContextResponse()


@app.route("/", context=[ctx_response])
def index(request):

    try:
        action = int(request.query['action'][0])
    except:
        action = 0

    if action == 1:
        ctx_response.messages.add_message('This is a message')
        ctx_response.messages.add_message('This is another message')
        raise http_exception.redirect('/', cookies=ctx_response.messages.response_cookies, status_code=303)
    elif action == 2:
        ctx_response.messages.error('This is an error message')
        raise http_exception.redirect('/', cookies=ctx_response.messages.response_cookies, status_code=303)
    elif action == 3:
        ctx_response.messages.success('This is an success message')
        raise http_exception.redirect('/', cookies=ctx_response.messages.response_cookies, status_code=303)

    return ctx_response.template('messages3.html')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
