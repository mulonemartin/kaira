from kaira.app import App
from kaira.response import response
from kaira.cookie import CookieManager

app = App()

options = {
    'HTTP_COOKIE_DOMAIN': '127.0.0.1',
    'HTTP_COOKIE_SECURE': False,
    'HTTP_COOKIE_HTTPONLY': False
}

menu = '''
        <h1>Index</h1>    
        <ul>
            <li><a href="%(index)s">Index</a></li>
            <li><a href="%(save)s">Save</a></li>
            <li><a href="%(delete)s">Delete</a></li>
        </ul>
        ''' % {
    'index': '/',
    'save': '/save',
    'delete': '/delete',
}


@app.route("/", name='index')
def index(request):
    cookie_val = request.cookies.get('cookie_example', None)
    if cookie_val:
        cookie_st = 'YES'
        cookie_key = 'cookie_example'
    else:
        cookie_st = 'NO'
        cookie_key = 'cookie_example'
        cookie_val = 'N/A'

    table = '''
    <table>
    <tr>
        <td>Cookie</td>        
        <td>Key</td>
        <td>Value</td>
    </tr>
    <tr>
        <td>%(cookie_st)s</td>        
        <td>%(cookie_key)s</td>
        <td>%(cookie_val)s</td>
    </tr>    
    </table>''' % {
        'cookie_st': cookie_st,
        'cookie_key': cookie_key,
        'cookie_val': cookie_val
    }
    html = menu + table

    return response.html(html)


@app.route("/save", name='save')
def save(request):
    cookies = CookieManager(options=options)
    cookies['cookie_example'] = 'value'
    cookies['cookie_example'].path = '/'

    return response.redirect('/', cookies=cookies)


@app.route("/delete", name='delete')
def delete(request):
    cookies = CookieManager(options=options)
    del cookies['cookie_example']

    return response.redirect('/', cookies=cookies)


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
