import logging
import logging.config
from inspect import stack, getmodulename
from traceback import format_exc

from kaira.log import log
from kaira.config import Config, LOGGING
from kaira.router import RouteHandler, PathRouter, RouteMethodHandler
from kaira.server import run
from kaira.wrapper import WrapWithContextManager
from kaira.request import HTTPRequest, HTTP_METHODS
from kaira.exceptions import BaseExceptionHTTP, ERR_DETAIL, ERR_CSS, ERR_TEMPLATE, \
    HTTPNotFound, HTTPMethodNotAllowed
from kaira.response import response as kaira_response
from kaira.statics import StaticHandler


class App:

    error_routes = dict()
    static_routes = dict()

    def __init__(self,
                 name=None,
                 router=None,
                 load_env=True,
                 log_config=LOGGING):
        if log_config:
            logging.config.dictConfig(log_config)
        # Only set up a default log handler if the
        # end-user application didn't set anything up.
        if not (logging.root.handlers and
                log.level == logging.NOTSET and
                log_config):
            formatter = logging.Formatter(
                "%(asctime)s: %(levelname)s: %(message)s")
            handler = logging.StreamHandler()
            handler.setFormatter(formatter)
            log.addHandler(handler)
            log.setLevel(logging.INFO)

        # Get name from previous stack frame
        if name is None:
            frame_records = stack()[1]
            name = getmodulename(frame_records[1])

        self.name = name
        self.config = Config(load_env=load_env)
        self.router = router or PathRouter()
        self.debug = None
        self.static_handler = None

    def static(self, route, path):
        """ get static"""

        if not self.static_handler:  # first time
            self.static_handler = StaticHandler(path, prefix=route)
            self.static_routes[route] = path
        else:
            if route not in self.static_routes:
                self.static_handler.add_files(path, prefix=route)
                self.static_routes[route] = path

    def error(self, status_code):
        """
            @app.error(500)
            def e_500():
                return 'Hello World'        
        """

        if 400 <= status_code <= 505:
            pass
        else:
            raise ValueError("Status code must be 400 <= code <= 505")

        def decorator(f):
            self.error_routes[status_code] = f
            return f

        return decorator

    def route(self, path,
              id_name=None,
              methods=frozenset({"GET"}),
              context=None,
              on_request=None,
              on_response=None):
        """
            @app.route('/')
            def index():
                return 'Hello World'        
        """

        def decorator(f):
            self.add_url_rule(path,
                              id_name=id_name,
                              route_func=f,
                              methods=methods,
                              context=context,
                              on_request=on_request,
                              on_response=on_response)
            return f

        return decorator

    def add_url_rule(self, path,
                     id_name=None,
                     route_func=None,
                     methods=frozenset({"GET"}),
                     context=None,
                     on_request=None,
                     on_response=None):
        """
        Basically this example::
            @app.route('/')
            def index():
                pass
        Is equivalent to the following::
            def index():
                pass
            app.add_url_rule('/', 'index', index)
        
        """

        if not path.endswith('/'):
            path += '/'

        methods = frozenset(map(lambda x: x.upper(), methods))

        if not frozenset(methods).issubset(frozenset(HTTP_METHODS)):
            raise ValueError("Not valid method. Only ('GET', 'POST', 'PUT', "
                             "'HEAD', 'OPTIONS', 'PATCH', 'DELETE')")

        wrapped_func = WrapWithContextManager(context)(route_func)

        # if already exist
        match_obj, match_dict = self.router.match(path)
        if match_obj:
            route_hand = match_obj
        else:
            route_hand = RouteHandler(path=path,
                                      id_name=id_name,
                                      route_func=route_func,
                                      methods=methods
                                      )

        for method in methods:
            route_method = RouteMethodHandler(func=wrapped_func,
                                              method=method,
                                              context=context,
                                              on_request=on_request,
                                              on_response=on_response)
            route_hand.handlers[method] = route_method

        if not match_obj:
            self.router.add_route(path, route_hand, name=route_hand.id_name)

        log.info('Route added. Path: %s Name: %s' % (path, route_hand.id_name))

    def dynamic_handler(self, environ, start_response):
        """Dynamic handler"""

        request = HTTPRequest(environ, 'utf-8')

        try:
            response = self.run_dispatcher(request)
        except BaseExceptionHTTP as e:
            if 400 <= e.status_code <= 505:
                if e.status_code in self.error_routes:
                    err_func = self.error_routes[e.status_code]
                    response = err_func(request)
                else:
                    err_css = ERR_CSS
                    err_detail = ERR_DETAIL[e.status_code]
                    err_code = e.status_code
                    err_explain = 'Oops error ocurred!.'
                    html_template = ERR_TEMPLATE.format(status_code=err_code,
                                                        status_detail=err_detail,
                                                        status_explain=err_explain,
                                                        err_css=err_css)
                    response = kaira_response.html(html_template, status_code=e.status_code)
            elif 300 <= e.status_code <= 307:
                kaira_response.redirect(e.absolute_url, e.status_code)
            else:
                raise NotImplemented("Invalid status code only 300 or 400 http codes")

        except Exception as e:
            err_code = 500
            err_css = ERR_CSS
            err_detail = ERR_DETAIL[err_code]
            err_explain_debug = "Error while handling error: {}\nStack: {}".format(
                e, format_exc())
            err_explain = "An error occurred while handling an error"
            if self.debug:
                err_explain = err_explain_debug
            log.error(err_explain_debug)
            html_template = ERR_TEMPLATE.format(status_code=err_code,
                                                status_detail=err_detail,
                                                status_explain=err_explain,
                                                err_css=err_css)
            response = kaira_response.html(html_template, status_code=err_code)

        return response.__call__(start_response)

    def run_dispatcher(self, request):
        """ Run dipatcher """

        response = None
        if not request.path.endswith('/'):
            request.path += '/'
        match_obj, match_dict = self.router.match(request.path)
        if match_obj:
            try:
                del match_dict['route_name']  # remove route_name key from dictionary
            except KeyError:
                pass

            try:
                method_handler = match_obj.handlers[request.method]
            except KeyError:
                raise HTTPMethodNotAllowed()

            if method_handler.on_request:
                for func_on_req in method_handler.on_request:
                    func_on_req(request)

            response = method_handler.func(request, **match_dict)

            if method_handler.on_response:
                for func_on_resp in method_handler.on_response:
                    func_on_resp(request, response)

        else:
            raise HTTPNotFound()

        return response

    def serve_static_handler(self, environ, start_response):
        """static handler"""

        try:
            response = self.static_handler.serve_static(environ, start_response)
            return response

        except BaseExceptionHTTP as e:
            request = HTTPRequest(environ, 'utf-8')
            if 400 <= e.status_code <= 505:
                if e.status_code in self.error_routes:
                    err_func = self.error_routes[e.status_code]
                    response = err_func(request)
                else:
                    err_css = ERR_CSS
                    err_detail = ERR_DETAIL[e.status_code]
                    err_code = e.status_code
                    err_explain = 'Oops error ocurred!.'
                    html_template = ERR_TEMPLATE.format(status_code=err_code,
                                                        status_detail=err_detail,
                                                        status_explain=err_explain,
                                                        err_css=err_css)
                    response = kaira_response.html(html_template, status_code=e.status_code)
            elif 300 <= e.status_code <= 307:
                kaira_response.redirect(e.absolute_url, e.status_code)
            else:
                raise NotImplemented("Invalid status code only 300 or 400 http codes")

            return response.__call__(start_response)

        except Exception as e:
            request = HTTPRequest(environ, 'utf-8')
            err_code = 500
            err_css = ERR_CSS
            err_detail = ERR_DETAIL[err_code]
            err_explain_debug = "Error while handling error: {}\nStack: {}".format(
                e, format_exc())
            err_explain = "An error occurred while handling an error"
            log.error(err_explain)
            if self.debug:
                err_explain = err_explain_debug
            html_template = ERR_TEMPLATE.format(status_code=err_code,
                                                status_detail=err_detail,
                                                status_explain=err_explain,
                                                err_css=err_css)
            response = kaira_response.html(html_template, status_code=err_code)

            return response.__call__(start_response)

    def wsgi_app(self, environ, start_response):
        """ """

        path_info = environ['PATH_INFO']
        registered_routes = self.static_routes.keys()
        static_match = path_info.startswith(tuple(registered_routes))

        if static_match:  # check if visitor has requested a static file
            return self.serve_static_handler(environ, start_response)
        else:  # else call the dynamic handler
            return self.dynamic_handler(environ, start_response)

    def __call__(self, environ, start_response):
        """Shortcut for :attr:`wsgi_app`."""

        return self.wsgi_app(environ, start_response)

    def run(self, debug=True, **kwargs):

        self.debug = debug
        log.info("Server started.. listening on host: %s:%s" % (kwargs['host'], kwargs['port']))
        run(self, **kwargs)

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.name,
        )

