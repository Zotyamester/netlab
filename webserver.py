from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from datetime import datetime, timezone
from functools import wraps

def run_server(hostname='', port=80, backlog=16):
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    server_address = (hostname, port)
    server_socket.bind(server_address)

    server_socket.listen(backlog)

    while True:
        client_socket, client_address = server_socket.accept()
        print("[%s]: New connection from: %s" % (datetime.now(timezone.utc).time(), client_address))
        handle_client(client_socket)

def handle_client(client_socket: socket):
    request_string = client_socket.recv(4096).decode('utf-8', 'replace')
    request = parse_request(request_string)
    response = handle_request(request)
    response_string = str(response)
    client_socket.send(response_string.encode())
    client_socket.close()

class Request:
    METHODS = {'OPTIONS', 'GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'TRACE', 'CONNECT'}
    HTTP_VERSIONS = {'HTTP/1.0', 'HTTP/1.1'}

    def __init__(self, method, uri, version, header_fields, body):
        self._method = method
        self._uri = uri
        self._version = version
        self._header_fields = header_fields
        self._body = body

    def handle(self):   
        if self._method != 'GET':
            return Response(403)
        if self._uri != '/':
            return Response(404)
        return Response(200, '<html><body>Hello, World!</body></html>')

def parse_request(request_string: str) -> Request | None:
    lines = request_string.split('\r\n')
    if len(lines) < 1:
        print('1')
        return None
    
    request_line = lines[0].split(' ')
    if len(request_line) != 3:
        print('2')
        return None
    
    method, uri, version = request_line
    if method not in Request.METHODS:
        print('3')
        return None
    if version not in Request.HTTP_VERSIONS:
        print('4')
        return None
    
    header_fields = dict()

    i = 1
    while i < len(lines) and lines[i] != '':
        header_line = lines[i].split(':')
        if len(header_line) < 2:
            return None
        
        header_name = header_line[0]
        header_value = ':'.join(header_line[1:]).strip()

        header_fields[header_name] = header_value

        i += 1

    if i >= len(lines) or lines[-1] != '':
        print('6')
        return None

    i += 1
    body = '\r\n'.join(lines[i:-1])

    return Request(method, uri, version, header_fields, body)

class Response:
    RESPONSE_CODES={
        100: 'Continue',
        101: 'Switching Protocols',
        200: 'OK',
        201: 'Created',
        202: 'Accepted',
        203: 'Non-Authoritative Information',
        204: 'No Content',
        205: 'Reset Content',
        206: 'Partial Content',
        300: 'Multiple Choices',
        301: 'Moved Permanently',
        302: 'Found',
        303: 'See Other',
        304: 'Not Modified',
        305: 'Use Proxy',
        307: 'Temporary Redirect',
        400: 'Bad Request',
        401: 'Unauthorized',
        402: 'Payment Required',
        403: 'Forbidden',
        404: 'Not Found',
        405: 'Method Not Allowed',
        406: 'Not Acceptable',
        407: 'Proxy Authentication Required',
        408: 'Request Time-out',
        409: 'Conflict',
        410: 'Gone',
        411: 'Length Required',
        412: 'Precondition Failed',
        413: 'Request Entity Too Large',
        414: 'Request-URI Too Large',
        415: 'Unsupported Media Type',
        416: 'Requested range not satisfiable',
        417: 'Expectation Failed',
        500: 'Internal Server Error',
        501: 'Not Implemented',
        502: 'Bad Gateway',
        503: 'Service Unavailable',
        504: 'Gateway Time-out',
        505: 'HTTP Version not supported extension-code',
    }

    def __init__(self, status_code: int, message_body: str='', version: str='HTTP/1.1'):
        self._status_code = status_code
        self._message_body = message_body
        self._version = version
        self._header_fields = {
            'Server': 'ZOLI/1.0',
            'Date': datetime.now(timezone.utc).strftime("%a, %d %b %G %T %Z"),
            'Content-Type': 'text/html',
        }

    def __str__(self) -> str:
        response_phrase = Response.RESPONSE_CODES[self._status_code]
        status_line = f'{self._version} {self._status_code} {response_phrase}'
        response_header = '\r\n'.join(f'{k}: {v}' for k, v in self._header_fields.items())
        return f'{status_line}\r\n{response_header}\r\n\r\n{self._message_body}\r\n\r\n'

def route(uri: str='/', methods: list[str]=Request.METHODS):
    '''returns a decorator function with the context of `uri` and `methods`'''

    def decorator_route(func):
        '''returns a wrapper function to `func` with a context of `uri` and `methods`, that has a guard clause for handling misdirected requests'''

        @wraps(func)
        def wrapper_route(request: Request, *args, **kwargs) -> Response | None:
            '''returns a response to the request (just like a regular handler `func` would do)'''
            
            if request._uri == uri and request._method in methods:
                return func(request, *args, **kwargs)
            return None
        return wrapper_route
    return decorator_route

@route('/', methods=['GET'])
def index(request):
    html = '''<!DOCTYPE html>
<html>
<head>
  <title>My little website!</title>
</head>
<body>
  <h1>Greetings! :D</h1>
  <p> Great little site, isn't it? </p>
  <a href="/cats">Kittens!</a>
</body>
</html>
'''
    return Response(200, html)

@route('/cats', methods=['GET'])
def cats(request):
    html = '''<!DOCTYPE html>
<html>
<head>
  <title>Hi, mom!</title>
</head>
<body>
  <h1>Cute cats!</h1>
  <img src="https://http.cat/200" alt="cutie" />
  <a href="/">Go back!</a>
</body>
</html>
'''
    return Response(200, html)

def handle_request(request: Request):
    registered_routes = [index, cats]
    if request == None:
        return Response(400)
    
    for registered_route in registered_routes:
        response = registered_route(request)
        if response != None:
            print(registered_route.__name__)
            return response
    
    return Response(404)

if __name__ == '__main__':
    run_server()
