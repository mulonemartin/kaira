from kaira.app import App
from kaira.response import response
from kaira.helpers import tag


app = App()


@app.route("/")
def hello_world(request):

    table = tag.table(_class='table table-striped jambo_table bulk_action')
    tr = tag.tr(_class='headings')
    tr.append(tag.th('Id', _class='column-title'))
    tr.append(tag.th('Correo', _class='column-title'))
    tr.append(tag.th('Usuario', _class='column-title'))
    tr.append(tag.th('Nombre', _class='column-title'))
    tr.append(tag.th('Apellido', _class='column-title'))
    tr.append(tag.th('Hab.', _class='column-title'))
    tr.append(tag.th('Fecha', _class='column-title'))
    tr.append(tag.th(tag.span('Accion', _class='nobr'), _class='column-title no-link last'))
    thead = tag.thead()
    thead.append(tr)
    table.append(thead)

    tbody = tag.tbody()

    return response.template('index.html', myname=table)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)

