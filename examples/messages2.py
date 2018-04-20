
from kaira.app import App
from kaira.response import response
from kaira.messages import MessagesManager, DEBUG, INFO, WARNING, ERROR, SUCCESS
from kaira.exceptions import http_exception
from kaira.wrapper import ContextManager


app = App()


class ContextMessages(ContextManager):
    messages_manager = None

    def __init__(self, options=None):
        self.options = options
        messages_manager = MessagesManager(options)
        self.messages_manager = messages_manager

    def on_start(self, request):
        self.messages_manager.start(request)

    def add_message(self, msg, lvl=INFO):
        self.messages_manager.add_message(msg, lvl)

    def info(self, msg):
        self.messages_manager.add_message(msg, msg_level=INFO)

    def debug(self, msg):
        self.messages_manager.add_message(msg, msg_level=DEBUG)

    def warning(self, msg):
        self.messages_manager.add_message(msg, msg_level=WARNING)

    def error(self, msg):
        self.messages_manager.add_message(msg, msg_level=ERROR)

    def success(self, msg):
        self.messages_manager.add_message(msg, msg_level=SUCCESS)

    def render(self):
        return self.messages_manager.render()

    @property
    def response_cookies(self):
        return self.messages_manager.response_cookies


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
