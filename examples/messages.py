
from kaira.app import App
from kaira.response import response
from kaira.messages import MessagesManager
from kaira.exceptions import http_exception


app = App()


@app.route("/")
def index(request):

    flash_messages = MessagesManager(request)
    flash_messages.load()

    try:
        action = int(request.query['action'][0])
    except:
        action = 0

    if action == 1:
        flash_messages.add_message('This is a message')
        flash_messages.add_message('This is another message')
        raise http_exception.redirect('/', cookies=flash_messages.response_cookies, status_code=303)
    elif action == 2:
        flash_messages.error('This is an error message')
        raise http_exception.redirect('/', cookies=flash_messages.response_cookies, status_code=303)
    elif action == 3:
        flash_messages.error('This is an success message')
        raise http_exception.redirect('/', cookies=flash_messages.response_cookies, status_code=303)

    return response.template('messages.html', cookies=flash_messages.response_cookies, flash_messages=flash_messages)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
