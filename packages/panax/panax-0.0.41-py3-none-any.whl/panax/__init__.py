import json, uuid, sys, os, datetime
sys.path.append(os.getcwd())

from config import APP_SETTING, PERMISSION_SETTING, PERMISSION_DEFAULT

from wsgiref.simple_server import make_server
from panax.request import Request
from panax.panax_views.auto_view import auto_config


url_map = {}


request = Request()


def run_server(environ, star_response):
    star_response('200 OK', [('Content-Type', 'application/json;charset=urf-8')])

    request.bind(environ)
    print(request.headers)

    request_path = request.path.replace('/api/', '')

    arr_path = str(request_path).split('/')

    if len(arr_path) != 2 and len(arr_path) != 3:
        response = json.dumps({"code": 404, "msg": "Not Found!"}).encode('utf-8')

    # 资源
    path_resource = arr_path[0]
    # 方法
    path_operation = arr_path[1]
    # 参数
    path_param = arr_path[2] if len(arr_path) == 3 else None

    # 请求地址 在url_map 中 已注册
    if path_resource in url_map and path_operation in url_map[path_resource]:
        if path_operation in url_map[path_resource]:
            func = url_map[path_resource][path_operation]

            if request.method not in func["method"]:
                response = json.dumps({"code": 405, "msg": "Method Not Allowed!"}).encode('utf-8')

            handle = func["handle"]
            if path_param is not None:
                result = handle(request, path_param)
            else:
                result = handle(request)

            response = json.dumps(result).encode('utf-8')
            return [response, ]
    else:
        if path_operation in auto_config:
            if request.method != "POST":
                response = json.dumps({"code": 405, "msg": "Method Not Allowed!"}).encode('utf-8')

            handle = auto_config[path_operation]

            if path_param is not None:
                result = handle(request, path_resource, path_param)
            else:
                result = handle(request, path_resource)

            response = json.dumps(result).encode('utf-8')
            return [response, ]
        else:
            response = json.dumps({"code": 404, "msg": "Not Found!"}).encode('utf-8')
            return [response, ]


def route(resource, operation, method=['POST']):
    def wrapper(handler):
        if resource not in url_map:
            url_map[resource] = {}

        url_map[resource][operation] = {
            "method": method,
            "handle": handler
        }
        return handler
    return wrapper


def run(host='127.0.0.1', port=8000, **kwargs):
    '''
    启动监听服务
    '''
    httpd = make_server(host, port, run_server)
    print('Courage server starting up ...')
    print('Listening on http://%s:%d/' % (host, port))
    print('Use Ctrl-C to quit.')
    print('')
    httpd.serve_forever()
