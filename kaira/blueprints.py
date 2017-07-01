from collections import namedtuple

BluprintRoute = namedtuple('Route',
                           ['path', 'name', 'handler', 'methods', 'context', 'on_request', 'on_response'])

BluprintStatic = namedtuple('Route',
                            ['route', 'path'])


class Blueprint:
    def __init__(self, name, url_prefix=None, host=None):
        """ """
        self.name = name
        self.url_prefix = url_prefix
        self.host = host

        self.routes = []
        self.statics = []

    def route(self, path,
              name=None,
              methods=frozenset({"GET"}),
              context=None,
              on_request=None,
              on_response=None):
        """ route """

        def decorator(handler):
            self.add_url_rule(path, name, handler, methods, context, on_request, on_response)
            return handler
        return decorator

    def add_url_rule(self, path,
                     name=None,
                     handler=None,
                     methods=frozenset({"GET"}),
                     context=None,
                     on_request=None,
                     on_response=None):
        """ """

        route = BluprintRoute(path, name, handler, methods, context, on_request, on_response)
        self.routes.append(route)

    def static(self, route, path):
        """ get static"""

        route = BluprintStatic(route, path)
        self.statics.append(route)

    def register(self, app, url_prefix=''):
        """ register on the app """

        # Routes
        for route in self.routes:
            # attach the blueprint name to the handler so that it can be
            # prefixed properly in the router
            route.handler.__blueprintname__ = self.name
            # Prepend the blueprint URI prefix if available
            if url_prefix:
                r_path = url_prefix + route.path
            else:
                r_path = route.path
            app.add_url_rule(r_path,
                             name=route.name,
                             handler=route.handler,
                             methods=route.methods,
                             context=route.context,
                             on_request=route.on_request,
                             on_response=route.on_response)

        # statics
        for static in self.statics:
            if url_prefix:
                s_route = url_prefix + static.route
            else:
                s_route = static.route

            app.static(s_route, static.path)
