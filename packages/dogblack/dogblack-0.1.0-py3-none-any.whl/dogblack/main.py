import json
import os
from pymongo import MongoClient
from werkzeug.wrappers import Response
from jinja2 import Environment, FileSystemLoader
from werkzeug.wsgi import SharedDataMiddleware

class MyFramework:
    def __init__(self, secret_token):
        self.routes = {}
        self.middleware = []
        self.client = MongoClient('localhost', 27017)  # Configuração do banco de dados MongoDB
        self.db = self.client.my_database  # Acesse seu banco de dados

        # Adicione o middleware de autenticação
        self.middleware.append(AuthMiddleware(secret_token))

        # Configuração do Jinja2 para templates
        template_path = os.path.join(os.path.dirname(__file__), 'templates')
        self.jinja_env = Environment(loader=FileSystemLoader(template_path))

        # Configuração para servir arquivos estáticos
        static_path = os.path.join(os.path.dirname(__file__), 'static')
        self.static_app = SharedDataMiddleware(None, {'/static': static_path})

    def route(self, path):
        def decorator(view_func):
            self.routes[path] = view_func
            return view_func
        return decorator

    def add_middleware(self, middleware):
        self.middleware.append(middleware)

    def __call__(self, environ, start_response):
        path = environ['PATH_INFO']

        # Verifica se a solicitação é para arquivos estáticos
        if path.startswith('/static'):
            return self.static_app(environ, start_response)

        for middleware in self.middleware:
            middleware.set_app(self)

        view_func = self.routes.get(path)
        if view_func:
            response = view_func(self, environ)
            return response(environ, start_response)
        else:
            response_body = 'Página não encontrada'
            status = '404 Not Found'
            response_headers = [('Content-type', 'text/plain')]
            start_response(status, response_headers)
            return [response_body.encode('utf-8')]

class AuthMiddleware:
    def __init__(self, secret_token):
        self.secret_token = secret_token

    def __call__(self, environ, start_response):
        auth_header = environ.get('HTTP_AUTHORIZATION', '')
        if auth_header != f'Bearer {self.secret_token}':
            start_response('401 Unauthorized', [('Content-type', 'text/plain')])
            return [b'Unauthorized']

        return self.app(environ, start_response)

    def set_app(self, app):
        self.app = app

class Router:
    def __init__(self):
        self.routes = {}

    def add_route(self, path, view_func):
        self.routes[path] = view_func

    def route(self, path):
        def decorator(view_func):
            self.add_route(path, view_func)
            return view_func
        return decorator

class Database:
    def __init__(self, host, port):
        self.client = MongoClient(host, port)
        self.db = self.client.my_database

    def insert_document(self, collection, data):
        return self.db[collection].insert_one(data)

    def find_documents(self, collection, query):
        return self.db[collection].find(query)

def json_response(data, status_code=200):
    response = Response(content_type='application/json', status=status_code)
    response.data = json.dumps(data)
    return response
