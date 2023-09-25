import cgi
import threading
from urllib.parse import parse_qs


class Request(threading.local):
    def bind(self, environ):
        self._environ = environ
        self._GET = None
        self._POST = None
        self._GETPOST = None
        self._COOKIES = None
        self.path = self._environ.get('PATH_INFO', '/').strip()
        if not self.path.startswith('/'):
            self.path = '/' + self.path

    @property
    def method(self):
        return self._environ.get('REQUEST_METHOD', 'GET').upper()

    @property
    def query_string(self):
        return self._environ.get('QUERY_STRING', '')

    @property
    def input_length(self):
        try:
            return int(self._environ.get('CONTENT_LENGTH', '0'))
        except ValueError:
            return 0

    @property
    def GET(self):
        if self._GET is None:
            raw_dict = parse_qs(self.query_string, keep_blank_values=1)
            self._GET = {}
            for key, value in raw_dict.items():
                if len(value) == 1:
                    self._GET[key] = value[0]
                else:
                    self._GET[key] = value
        return self._GET

    @property
    def POST(self):
        if self._POST is None:
            raw_data = cgi.FieldStorage(fp=self._environ['wsgi.input'], environ=self._environ)
            self._POST = {}
            if raw_data.list:
                for key in raw_data:
                    if raw_data[key].filename:
                        self._POST[key] = raw_data[key]
                    elif isinstance(raw_data[key], list):
                        self._POST[key] = [v.value for v in raw_data[key]]
                    else:
                        self._POST[key] = raw_data[key].value
        return self._POST

    @property
    def params(self):
        if self._GETPOST is None:
            self._GETPOST = dict(self.GET)
            self._GETPOST.update(self.POST)
