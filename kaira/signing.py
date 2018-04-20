import base64
import datetime
import json
import re
import time
import zlib
from decimal import Decimal
import hmac
import hashlib

from kaira.baseconv import base62

_PROTECTED_TYPES = (
    type(None), int, float, Decimal, datetime.datetime, datetime.date, datetime.time,
)
_SEP_UNSAFE = re.compile(r'^[A-z0-9-_=]*$')


def is_protected_type(obj):
    """Determine if the object instance is of a protected type.
    Objects of protected types are preserved as-is when passed to
    force_text(strings_only=True).
    """
    return isinstance(obj, _PROTECTED_TYPES)


def force_bytes(s, encoding='utf-8', strings_only=False, errors='strict'):
    """
    Similar to smart_bytes, except that lazy instances are resolved to
    strings, rather than kept as lazy objects.
    If strings_only is True, don't convert (some) non-string-like objects.
    """
    # Handle the common case first for performance reasons.
    if isinstance(s, bytes):
        if encoding == 'utf-8':
            return s
        else:
            return s.decode('utf-8', errors).encode(encoding, errors)
    if strings_only and is_protected_type(s):
        return s
    if isinstance(s, memoryview):
        return bytes(s)
    if not isinstance(s, str):
        return str(s).encode(encoding, errors)
    else:
        return s.encode(encoding, errors)


class BadSignature(Exception):
    """Signature does not match."""
    pass


class SignatureExpired(BadSignature):
    """Signature timestamp is older than required max_age."""
    pass


def salted_hmac(key_salt, value, secret=None):
    """
    Return the HMAC-SHA1 of 'value', using a key generated from key_salt and a
    secret (which defaults to settings.SECRET_KEY).
    A different key_salt should be passed in for every application of HMAC.
    """
    if secret is None:
        secret = b'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm'

    key_salt = force_bytes(key_salt)
    secret = force_bytes(secret)

    # We need to generate a derived key from our base key.  We can do this by
    # passing the key_salt and our base key through a pseudo-random function and
    # SHA1 works nicely.
    key = hashlib.sha1(key_salt + secret).digest()

    # If len(key_salt + secret) > sha_constructor().block_size, the above
    # line is redundant and could be replaced by key = key_salt + secret, since
    # the hmac module does the same thing for keys longer than the block size.
    # However, we need to ensure that we *always* do this.
    return hmac.new(key, msg=force_bytes(value), digestmod=hashlib.sha1)


def constant_time_compare(val1, val2):
    """Return True if the two strings are equal, False otherwise."""
    return hmac.compare_digest(force_bytes(val1), force_bytes(val2))


def b64_encode(s):
    return base64.urlsafe_b64encode(s).strip(b'=')


def b64_decode(s):
    pad = b'=' * (-len(s) % 4)
    return base64.urlsafe_b64decode(s + pad)


def base64_hmac(salt, value, key):
    return b64_encode(salted_hmac(salt, value, key).digest()).decode()


class JSONSerializer:
    """
    Simple wrapper around json to be used in signing.dumps and
    signing.loads.
    """
    def dumps(self, obj):
        return json.dumps(obj, separators=(',', ':')).encode('latin-1')

    def loads(self, data):
        return json.loads(data.decode('latin-1'))


def dumps(obj, key=None, salt='kaira.sessions', serializer=JSONSerializer, compress=False):
    """
    Return URL-safe, hmac/SHA1 signed base64 compressed JSON string. If key is
    None, use settings.SECRET_KEY instead.
    If compress is True (not the default), check if compressing using zlib can
    save some space. Prepend a '.' to signify compression. This is included
    in the signature, to protect against zip bombs.
    Salt can be used to namespace the hash, so that a signed string is
    only valid for a given namespace. Leaving this at the default
    value or re-using a salt value across different parts of your
    application without good cause is a security risk.
    The serializer is expected to return a bytestring.
    """
    data = serializer().dumps(obj)

    # Flag for if it's been compressed or not
    is_compressed = False

    if compress:
        # Avoid zlib dependency unless compress is being used
        compressed = zlib.compress(data)
        if len(compressed) < (len(data) - 1):
            data = compressed
            is_compressed = True
    base64d = b64_encode(data).decode()
    if is_compressed:
        base64d = '.' + base64d
    return TimestampSigner(key, salt=salt).sign(base64d)


def loads(s, key=None, salt='kaira.sessions', serializer=JSONSerializer, max_age=None):
    """
    Reverse of dumps(), raise BadSignature if signature fails.
    The serializer is expected to accept a bytestring.
    """
    # TimestampSigner.unsign() returns str but base64 and zlib compression
    # operate on bytes.
    base64d = TimestampSigner(key, salt=salt).unsign(s, max_age=max_age).encode()
    decompress = base64d[:1] == b'.'
    if decompress:
        # It's compressed; uncompress it first
        base64d = base64d[1:]
    data = b64_decode(base64d)
    if decompress:
        data = zlib.decompress(data)
    return serializer().loads(data)


class Signer:

    def __init__(self, key=None, sep=':', salt=None):
        # Use of native strings in all versions of Python
        self.key = key or 'APj00jpfj8Gx1SjnyLxwBBSQfnQ9DJYe0Cm'
        self.sep = sep
        if _SEP_UNSAFE.match(self.sep):
            raise ValueError(
                'Unsafe Signer separator: %r (cannot be empty or consist of '
                'only A-z0-9-_=)' % sep,
            )
        self.salt = salt or '%s.%s' % (self.__class__.__module__, self.__class__.__name__)

    def signature(self, value):
        return base64_hmac(self.salt + 'signer', value, self.key)

    def sign(self, value):
        return '%s%s%s' % (value, self.sep, self.signature(value))

    def unsign(self, signed_value):
        if self.sep not in signed_value:
            raise BadSignature('No "%s" found in value' % self.sep)
        value, sig = signed_value.rsplit(self.sep, 1)
        if constant_time_compare(sig, self.signature(value)):
            return value
        raise BadSignature('Signature "%s" does not match' % sig)


class TimestampSigner(Signer):

    def timestamp(self):
        return base62.encode(int(time.time()))

    def sign(self, value):
        value = '%s%s%s' % (value, self.sep, self.timestamp())
        return super().sign(value)

    def unsign(self, value, max_age=None):
        """
        Retrieve original value and check it wasn't signed more
        than max_age seconds ago.
        """
        result = super().unsign(value)
        value, timestamp = result.rsplit(self.sep, 1)
        timestamp = base62.decode(timestamp)
        if max_age is not None:
            if isinstance(max_age, datetime.timedelta):
                max_age = max_age.total_seconds()
            # Check timestamp is not older than max_age
            age = time.time() - timestamp
            if age > max_age:
                raise SignatureExpired(
                    'Signature age %s > %s seconds' % (age, max_age))
        return value
