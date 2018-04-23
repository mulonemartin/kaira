
from kaira.app import App
from kaira.response import response
from kaira.messages import ContextMessages
from kaira.exceptions import http_exception


app = App()


context_messages = ContextMessages()


@app.route("/", context=[context_messages])
def index(request):

    try:
        action = int(request.query['action'][0])
    except:
        action = 0

    if action == 1:
        context_messages.add_message('This is a message')
        context_messages.add_message('This is another message')
        raise http_exception.redirect('/', cookies=context_messages.response_cookies, status_code=303)
    elif action == 2:
        context_messages.error('This is an error message')
        raise http_exception.redirect('/', cookies=context_messages.response_cookies, status_code=303)
    elif action == 3:
        context_messages.error('This is an success message')
        raise http_exception.redirect('/', cookies=context_messages.response_cookies, status_code=303)

    return response.template('messages.html', cookies=context_messages.response_cookies, flash_messages=context_messages)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
