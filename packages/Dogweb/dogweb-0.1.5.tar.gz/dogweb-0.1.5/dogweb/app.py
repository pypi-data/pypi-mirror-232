from jinja2 import Environment, FileSystemLoader
from werkzeug.wrappers import Request, Response
from werkzeug.routing import Map, Rule
import os

class MeuFramework:
    def __init__(self, template_dir='templates', static_dir='static'):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.static_dir = static_dir
        self.url_map = Map()
        self.routes = {}

    def route(self, path):
        def decorator(view_func):
            rule = Rule(path, endpoint=view_func.__name__)
            self.url_map.add(rule)
            self.routes[view_func.__name__] = view_func
            return view_func
        return decorator

    def render_template(self, template_name, context={}):
        template = self.env.get_template(template_name)
        return template.render(context)

    def static(self, filename):
        return f'{self.static_dir}/{filename}'

    def __call__(self, environ, start_response):
        request = Request(environ)
        adapter = self.url_map.bind_to_environ(request.environ)
        endpoint, values = adapter.match()
        response = self.handle_request(request, endpoint, values)
        return response(environ, start_response)

    def handle_request(self, request, endpoint, values):
        view_func = self.routes.get(endpoint)
        if view_func:
            context = {
                'titulo': 'Título da Página',
                'conteudo': 'Conteúdo da Página',
            }
            html_output = self.render_template('template.html', context)
            return Response(html_output, content_type='text/html')
        elif endpoint == 'static':
            filename = values['filename']
            file_path = self.static(filename)
            return Response(open(file_path, 'rb').read(), content_type='text/plain')
        else:
            return Response('Página não encontrada', content_type='text/plain', status=404)
