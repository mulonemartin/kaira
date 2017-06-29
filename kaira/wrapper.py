
__all__ = ['ContextManager', 'WrapWithContextManager']


class ContextManager(object):
    name = 'ContextManager'

    def on_start(self, request):
        pass

    def on_success(self, request):
        pass

    def on_failure(self, request):
        pass

    def wrap_call(self, func):
        return func


class WrapWithContextManager(object):

    def __init__(self, context=None, skip_list=None):
        self.context = context
        if skip_list is None:
            skip_list = []
        self.skip_list = skip_list

    def __call__(self, f):
        def wrap(fnc, ctm):
            def g(*a, **b):
                try:
                    ctm.on_start(a[0])
                    output = ctm.wrap_call(fnc)(*a, **b)
                    ctm.on_success(a[0])
                    return output

                except:
                    ctm.on_failure(a[0])
                    raise

            return g

        def wrap_skip_context(fnc, ctm):
            def g(*a, **b):
                output = ctm.wrap_call(fnc)(*a, **b)
                return output

            return g

        if self.context:
            for context in reversed(self.context):
                if isinstance(context, ContextManager):
                    if context.name in self.skip_list:
                        f = wrap_skip_context(f, context)
                    else:
                        f = wrap(f, context)

        return f
