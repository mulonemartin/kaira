import os
from whitenoise import WhiteNoise
from whitenoise.utils import decode_path_info

from .exceptions import HTTPNotFound
from .log import log


PACKAGE_STATICS = os.path.join(os.path.dirname(__file__), "static")


class StaticHandler:
    """ Static handler """

    def __init__(self, root_dir=PACKAGE_STATICS, prefix='static'):
        """ Init"""

        self.whitenoise = WhiteNoise(application=None, root=root_dir, prefix=prefix)

    def add_files(self, path, prefix='static'):
        """ Add files"""

        self.whitenoise.add_files(path, prefix)

    def serve_static(self, environ, start_response):

        log.info("ENTRA>>>>")
        path = decode_path_info(environ['PATH_INFO'])
        if self.whitenoise.autorefresh:
            static_file = self.whitenoise.find_file(path)
        else:
            static_file = self.whitenoise.files.get(path)
        if static_file is None:
            raise HTTPNotFound()
        else:
            log.info("ENTRA>>>>222")
            return self.whitenoise.serve(static_file, environ, start_response)
