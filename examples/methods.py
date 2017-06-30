
from kaira.app import App
from kaira.response import response


app = App()


@app.route("/", methods=['GET'])
def hello_world(request):
    return response.text('Hello World!')


@app.route("/form", methods=['GET', 'POST'])
def form(request):
    return response.text('Hello World!')


@app.route("/data", methods=['GET'])
def get_form(request):
    return response.text('Data for get method!')


@app.route("/data", methods=['POST'])
def post_form(request):
    return response.text('Data for post method!')


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
