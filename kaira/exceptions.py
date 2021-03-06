
class BaseExceptionHTTP(Exception):

    default_status_code = 500
    default_detail = 'Server error'

    def __init__(self, detail=None, status_code=None):
        super().__init__(detail)

        self.detail = self.default_detail if (detail is None) else detail
        self.status_code = self.default_status_code if (status_code is None) else status_code


class HTTPError(BaseExceptionHTTP):
    default_status_code = 500
    default_detail = 'Server error'
    cookies = None
    headers = None
    content_type = 'text'

    def __init__(self, detail=None, status_code=None, cookies=None, headers=None, content_type='text'):
        super().__init__(detail=detail, status_code=status_code)

        self.cookies = cookies
        self.header = headers
        self.content_type = content_type


class HTTPRedirect(BaseExceptionHTTP):

    default_status_code = 302
    default_detail = ''
    cookies = None
    headers = None

    def __init__(self, absolute_url, detail=None, status_code=None, cookies=None, headers=None):

        super().__init__(detail, status_code)
        self.absolute_url = absolute_url
        self.cookies = cookies
        self.header = headers


class HTTPNotFound(BaseExceptionHTTP):
    default_status_code = 404
    default_detail = 'Not found'


class HTTPMethodNotAllowed(BaseExceptionHTTP):
    default_status_code = 405
    default_detail = 'Method Not Allowed'


class HandleException:

    @staticmethod
    def redirect(absolute_url, detail=None, status_code=None, cookies=None, headers=None):
        """ redirect """

        resp = HTTPRedirect(absolute_url, detail=detail, status_code=status_code,
                            cookies=cookies, headers=headers)
        return resp

    @staticmethod
    def json(body, status_code=None, cookies=None, headers=None):
        """ json """

        resp = HTTPError(body, status_code=status_code, cookies=cookies,
                         headers=headers, content_type='json')
        return resp

    @staticmethod
    def text(body, status_code=None, cookies=None, headers=None):
        """ text """

        resp = HTTPError(body, status_code=status_code, cookies=cookies,
                         headers=headers, content_type='text')
        return resp


http_exception = HandleException()


ERR_DETAIL = {
    # Client Error
    400: 'Bad Request',
    401: 'Unauthorized',
    402: 'Payment Required',
    403: 'Forbidden',
    404: 'Not Found',
    405: 'Method Not Allowed',
    406: 'Not Acceptable',
    407: 'Proxy Authentication Required',
    408: 'Request Timeout',
    409: 'Conflict',
    410: 'Gone',
    411: 'Length Required',
    412: 'Precondition Failed',
    413: 'Request Entity Too Large',
    414: 'Request-Uri Too Long',
    415: 'Unsupported Media Type',
    416: 'Requested Range Not Satisfiable',
    417: 'Expectation Failed',
    # Server Error
    500: 'Internal Server Error',
    501: 'Not Implemented',
    502: 'Bad Gateway',
    503: 'Service Unavailable',
    504: 'Gateway Timeout',
    505: 'Http Version Not Supported'
}

ERR_CSS = '''
<style type="text/css">/*! normalize.css v5.0.0 | MIT License | github.com/necolas/normalize.css */html{font-family:sans-serif;line-height:1.15;-ms-text-size-adjust:100%;-webkit-text-size-adjust:100%}body{margin:0}article,aside,footer,header,nav,section{display:block}h1{font-size:2em;margin:.67em 0}figcaption,figure,main{display:block}figure{margin:1em 40px}hr{box-sizing:content-box;height:0;overflow:visible}pre{font-family:monospace,monospace;font-size:1em}a{background-color:transparent;-webkit-text-decoration-skip:objects}a:active,a:hover{outline-width:0}abbr[title]{border-bottom:none;text-decoration:underline;text-decoration:underline dotted}b,strong{font-weight:inherit}b,strong{font-weight:bolder}code,kbd,samp{font-family:monospace,monospace;font-size:1em}dfn{font-style:italic}mark{background-color:#ff0;color:#000}small{font-size:80%}sub,sup{font-size:75%;line-height:0;position:relative;vertical-align:baseline}sub{bottom:-.25em}sup{top:-.5em}audio,video{display:inline-block}audio:not([controls]){display:none;height:0}img{border-style:none}svg:not(:root){overflow:hidden}button,input,optgroup,select,textarea{font-family:sans-serif;font-size:100%;line-height:1.15;margin:0}button,input{overflow:visible}button,select{text-transform:none}[type=reset],[type=submit],button,html [type=button]{-webkit-appearance:button}[type=button]::-moz-focus-inner,[type=reset]::-moz-focus-inner,[type=submit]::-moz-focus-inner,button::-moz-focus-inner{border-style:none;padding:0}[type=button]:-moz-focusring,[type=reset]:-moz-focusring,[type=submit]:-moz-focusring,button:-moz-focusring{outline:1px dotted ButtonText}fieldset{border:1px solid silver;margin:0 2px;padding:.35em .625em .75em}legend{box-sizing:border-box;color:inherit;display:table;max-width:100%;padding:0;white-space:normal}progress{display:inline-block;vertical-align:baseline}textarea{overflow:auto}[type=checkbox],[type=radio]{box-sizing:border-box;padding:0}[type=number]::-webkit-inner-spin-button,[type=number]::-webkit-outer-spin-button{height:auto}[type=search]{-webkit-appearance:textfield;outline-offset:-2px}[type=search]::-webkit-search-cancel-button,[type=search]::-webkit-search-decoration{-webkit-appearance:none}::-webkit-file-upload-button{-webkit-appearance:button;font:inherit}details,menu{display:block}summary{display:list-item}canvas{display:inline-block}template{display:none}[hidden]{display:none}/*! Simple HttpErrorPages | MIT X11 License | https://github.com/AndiDittrich/HttpErrorPages */body,html{width:100%;height:100%;background-color:#21232a}body{color:#fff;text-align:center;text-shadow:0 2px 4px rgba(0,0,0,.5);padding:0;min-height:100%;-webkit-box-shadow:inset 0 0 75pt rgba(0,0,0,.8);box-shadow:inset 0 0 75pt rgba(0,0,0,.8);display:table;font-family:"Open Sans",Arial,sans-serif}h1{font-family:inherit;font-weight:500;line-height:1.1;color:inherit;font-size:36px}h1 small{font-size:68%;font-weight:400;line-height:1;color:#777}a{text-decoration:none;color:#fff;font-size:inherit;border-bottom:dotted 1px #707070}.lead{color:silver;font-size:21px;line-height:1.4}.cover{display:table-cell;vertical-align:middle;padding:0 20px}footer{position:fixed;width:100%;height:40px;left:0;bottom:0;color:#a0a0a0;font-size:14px}</style>
'''

ERR_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Simple HttpErrorPages | MIT X11 License | https://github.com/AndiDittrich/HttpErrorPages -->

    <meta charset="utf-8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    
    <title>We've got some trouble | {status_code} - {status_detail}</title>

    {err_css}
    
</head>

<body>
    <div class="cover">
        <h1>{status_detail} <small>Error {status_code}</small></h1>
        <p class="lead">{status_explain}.</p>
    </div>
    
    </body>
</html>

'''
