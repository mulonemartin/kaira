""" Flash module """


# import datetime
# from datetime import timedelta
#
#
# class BaseFlashManager(object):
#     """Flash Manager"""
#
#     def __init__(self, request, msg, status, cookies=None, options=None):
#         """ Init """
#
#         self.request = request
#         self.cookies = cookies
#         self.msg = msg
#         self.status = status
#
#         if not options:
#             options = {
#                 'FLASH_COOKIE_DOMAIN': '',
#                 'FLASH_COOKIE_SECURE': False,
#                 'FLASH_COOKIE_HTTPONLY': True,
#                 'FLASH_COOKIE_EXPIRE': 600,
#                 'FLASH_COOKIE_PATH': '/',
#                 'FLASH_COOKIE_NAME': 'kaira_flash',
#                 'FLASH_SECRET': b'APj00cpfa8Gx1SjnyLxwBBSQfnQ9DJYe0Cm',
#                 'FLASH_TIME_LIMIT': timedelta(minutes=60)
#             }
#
#         self.options = options
#
#     def save(self):
#         """Save"""
#
#         expire_seconds = int(self.options['FLASH_COOKIE_EXPIRE'])
#         if expire_seconds > 0:
#             now = datetime.datetime.utcnow()
#             expires_cookie = now + datetime.timedelta(seconds=expire_seconds)
#         else:
#             expires_cookie = None
#
#         if not self.options['FLASH_COOKIE_DOMAIN'] or self.options['FLASH_COOKIE_DOMAIN'] == "":
#             domain = self.request.host.split(':')[0]
#         else:
#             domain = self.options['FLASH_COOKIE_DOMAIN']
#
#         cookies_options = {
#             'HTTP_COOKIE_DOMAIN': domain,
#             'HTTP_COOKIE_SECURE': self.options['FLASH_COOKIE_SECURE'],
#             'HTTP_COOKIE_HTTPONLY': self.options['FLASH_COOKIE_HTTPONLY']
#         }
#
#         cookie_name = self.options['FLASH_COOKIE_NAME']
#         time_limit = meta.csrf_options['FLASH_TIME_LIMIT']
#         csrf_secret = meta.csrf_options['CSRF_SECRET']
#
#         rand_code = None
#         if request.cookies:
#             if cookie_name in request.cookies:
#                 rand_code = request.cookies[cookie_name]
#
#         if not rand_code:
#             rand_code = sha1(os.urandom(64)).hexdigest()
#
#         if time_limit:
#             expires = (self.now() + time_limit).strftime(self.TIME_FORMAT)
#             csrf_build = '%s%s' % (rand_code, expires)
#         else:
#             expires = ''
#             csrf_build = rand_code
#
#         hmac_csrf = hmac.new(csrf_secret, csrf_build.encode('utf8'), digestmod=sha1)
#         value_csrf = '%s##%s' % (expires, hmac_csrf.hexdigest())
#
#         cookies = meta.cookies
#         if not cookies:
#             cookies = CookieManager(options=cookies_options)
#
#         cookies[cookie_name] = rand_code
#         cookies[cookie_name].path = meta.csrf_options['CSRF_COOKIE_PATH']
#         cookies[cookie_name].expires = expires_cookie
#
#         meta.cookies = cookies
