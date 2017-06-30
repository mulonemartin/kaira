""" ``router`` module.
"""

import os

from warnings import warn

from kaira.routing.builders import build_route
from kaira.routing.config import route_builders as default_route_builders
from kaira.routing.utils import route_name


class RouteMethodHandler:

    def __init__(self,
                 func=None,
                 method=frozenset({"GET"}),
                 context=None,
                 on_request=None,
                 on_response=None
                 ):
        self.func = func
        self.method = method
        self.context = context
        self.on_request = on_request
        self.on_response = on_response


class RouteHandler(object):
    """ Route handler """

    def __init__(self,
                 path=None,
                 name=None,
                 route_func=None,
                 methods=frozenset({"GET"})
                 ):

        self.handlers = dict()
        self.path = path
        self.name = name
        self.route_func = route_func
        self.methods = methods

        if not route_func:
            raise ValueError('You must pass a function')

        self.func_name = self.route_func.__name__
        self.filename = route_func.__code__.co_filename
        mtime = os.path.getmtime(self.filename)

        if self.path:
            self.path = '/' + self.route_func.__name__ + '(.\w+)?'
        if not self.name:
            self.name = self.func_name
        if not self.path.startswith('/'):
            self.path = '/' + self.path
        if not self.path.endswith('/'):
            self.path = self.path + '/'


def url(pattern, handler, kwargs=None, name=None):
    """ Converts parameters to tupple of length four.
        Used for convenience to name parameters and skip
        unused.
    """
    return pattern, handler, kwargs, name


class PathRouter(object):
    """
    """

    __slots__ = ('mapping', 'match_map', 'path_map', 'inner_path_map',
                 'route_builders')

    def __init__(self, route_builders=None):
        """
        """
        self.route_builders = route_builders or default_route_builders
        # match
        self.match_map = {}
        self.mapping = []
        # path
        self.path_map = {}
        self.inner_path_map = {}

    def add_route(self, pattern, handler, kwargs=None, name=None):
        """ Adds a pattern to route table
        """
        name = name or route_name(handler)
        if name in self.path_map:  # pragma: nocover
            warn('PathRouter: overriding route: %s.' % name)
        # build finishing route
        route = build_route(pattern, True, kwargs, name, self.route_builders)
        self.path_map[name] = route.path
        if route.exact_matches:
            for pattern, kwargs in route.exact_matches:
                if pattern in self.match_map:  # pragma: nocover
                    warn('PathRouter: overriding path: %s.' % pattern)
                self.match_map[pattern] = (handler, kwargs)
            route.exact_matches = None
        else:
            self.mapping.append((route.match, handler))

    def include(self, pattern, included, kwargs=None):
        """ Includes nested routes below the current.
        """
        # try build intermediate route
        route = build_route(pattern, False, kwargs, None, self.route_builders)
        if not isinstance(included, PathRouter):
            router = PathRouter(self.route_builders)
            router.add_routes(included)
            included = router
        if route.exact_matches:
            for p, kwargs in route.exact_matches:
                for k, v in included.match_map.items():
                    k = p + k
                    if k in self.match_map:  # pragma: nocover
                        warn('PathRouter: overriding path: %s.' % k)
                    h, kw = v
                    self.match_map[k] = (h, dict(kwargs, **kw))
            route.exact_matches = None
            included.match_map = {}
            if included.mapping:
                self.mapping.append((route.match, included))
        else:
            self.mapping.append((route.match, included))
        route_path = route.path
        for name, path in included.path_map.items():
            if name in self.inner_path_map:  # pragma: nocover
                warn('PathRouter: overriding route: %s.' % name)
            self.inner_path_map[name] = (route_path, path)
        included.path_map = None
        for name, paths in included.inner_path_map.items():
            if name in self.inner_path_map:  # pragma: nocover
                warn('PathRouter: overriding route: %s.' % name)
            self.inner_path_map[name] = tuple([route_path] + list(paths))
        included.inner_path_map = None
        # print('include %s => %s / %s' % (pattern, len(self.match_map),
        #                                 len(included.mapping)))

    def add_routes(self, mapping):
        """ Adds routes represented as a list of tuple
            (pattern, handler, kwargs=None, name=None) to route table.
        """
        for m in mapping:
            l = len(m)
            kwargs, name = None, None
            if l == 2:
                pattern, handler = m
            elif l == 3:
                pattern, handler, kwargs = m
            else:
                pattern, handler, kwargs, name = m
            if isinstance(handler, (tuple, list, PathRouter)):
                self.include(pattern, handler, kwargs)
            else:
                self.add_route(pattern, handler, kwargs, name)
        # print('add_routes => %s / %s' % (len(self.match_map),
        #                                 len(self.mapping)))

    def match(self, path):
        """ Tries to find a match for the given path in route table.
            Returns a tupple of (handler, kwargs)
        """
        if path in self.match_map:
            return self.match_map[path]
        for match, handler in self.mapping:
            matched, kwargs = match(path)
            if matched >= 0:
                # TODO: isinstance(handler, PathRouter)
                match = getattr(handler, 'match', None)
                if not match:
                    return handler, kwargs
                handler, kwargs_inner = match(path[matched:])
                if handler:
                    if not kwargs:
                        return handler, kwargs_inner
                    if kwargs_inner:
                        kwargs = dict(kwargs, **kwargs_inner)
                    return handler, kwargs
        return None, {}

    def path_for(self, name, **kwargs):
        """ Returns the url for the given route name.
        """
        if name in self.path_map:
            return self.path_map[name](kwargs)
        else:
            return ''.join([path(kwargs) for path
                            in self.inner_path_map[name]])
