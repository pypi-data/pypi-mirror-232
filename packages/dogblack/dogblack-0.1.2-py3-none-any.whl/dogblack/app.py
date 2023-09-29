# my_framework/my_framework/framework.py
class MyFramework:
    def __init__(self):
        self.routes = {}

    def route(self, path):
        def decorator(view_func):
            self.routes[path] = view_func
            return view_func
        return decorator

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']
        view_func = self.routes.get(path)
        if view_func:
            response_body = view_func()
            status = '200 OK'
        else:
            response_body = 'Página não encontrada'
            status = '404 Not Found'

        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)

        return [response_body.encode('utf-8')]
