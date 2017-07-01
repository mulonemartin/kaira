
from kaira.app import App
from kaira.blueprints import Blueprint
from kaira.response import response


app = App()

bp = Blueprint('Blueprint_1')
bp2 = Blueprint('Blueprint_2')


@bp.route("/")
def bp_index(request):
    return response.text('Hello World! bp: index')


@bp.route("/index2")
def bp_index2(request):
    return response.text('Hello World! bp: index2 ')


@bp2.route("/bp")
def bp2_index(request):
    return response.text('Hello World! bp2: index')


@bp2.route("/bp/index2")
def bp2_index2(request):
    return response.text('Hello World! bp2: index2 ')


bp.register(app)
bp2.register(app)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
