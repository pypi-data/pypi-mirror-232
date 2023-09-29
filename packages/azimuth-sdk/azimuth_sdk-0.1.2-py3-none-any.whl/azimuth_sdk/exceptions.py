import re

from httpx import codes


class SDKError(Exception):
    """
    Base class for errors raised by the SDK.
    """


class APIErrorMeta(type):
    """
    Metaclass for the API error type.
    """
    __exceptions__ = {}

    def __new__(cls, name, bases, attrs, status_code = None):
        klass = super().__new__(cls, name, bases, attrs)
        klass.__status_code__ = status_code
        return klass

    def __getitem__(cls, code):
        if code not in cls.__exceptions__:
            name = re.sub(r"[^a-zA-Z0-9]", "", codes.get_reason_phrase(code))
            klass = type(name, (APIError, ), {}, status_code = code)
            cls.__exceptions__[code] = klass
        return cls.__exceptions__[code]

    def __call__(cls, source):
        status_code = source.response.status_code
        # If the status code already matches the source, we are done
        if getattr(cls, "__status_code__", None) == status_code:
            return super().__call__(source)
        else:
            return cls[status_code](source)


class APIError(SDKError, metaclass = APIErrorMeta):
    """
    Base class for Azimuth API errors.
    """
    def __init__(self, source):
        super().__init__(source.response.text)
        self.request = source.request
        self.response = source.response

    @property
    def status_code(self):
        """
        The status code of the error.
        """
        return self.response.status_code

    @property
    def reason_phrase(self):
        """
        The reason phrase for the error.
        """
        return self.response.reason_phrase
