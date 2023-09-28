from __future__ import annotations

import os.path
import re
from collections import defaultdict
from typing import Callable, ClassVar, Literal

from markupsafe import Markup
from starlette.templating import Jinja2Templates
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route, Mount
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.config import Config
from starlette.staticfiles import StaticFiles
from . import ctx, keymodel, form, middleware, model, db, element, jinja


class App(Starlette):
    ACTIONS: ClassVar[tuple[str]] = ('create', 'update', 'list', 'search', 'detail', 'select-options', 'datalist-options')
    MICROS: ClassVar[tuple[str]] = ('get', 'post', 'base', 'public')
    def __init__(self, *args, **kwargs):
        routes = kwargs.pop('routes', [])
        self._templates = jinja.templates
        
        self.config = Config(os.path.join(os.getcwd(), kwargs.pop('env', None)))
        
        if static := kwargs.pop('static', None):
            self.static = StaticFiles(directory=os.path.join(os.getcwd(), static))
            routes.append(self.static_mount())
        
        self.context = ctx.context
        
        kwargs['routes'] = routes
        middle = kwargs.pop('middleware', [])
        middle.extend(middleware.middleware)
        kwargs['routes'] = routes
        kwargs['middleware'] = middle
        super().__init__(*args, **kwargs)
        
    @property
    def templates(self):
        return self._templates
    
    def extend_routes(self, routes: list[Route | Mount]):
        self.routes.extend(routes)
    
    def append_route(self, path: str, endpoint: Callable, name=None, methods=None):
        self.routes.append(Route(path, endpoint=endpoint, name=name, methods=methods if methods else ['GET']))
    
    def append_mount(self, path: str, app=None, routes=None, name=None):
        if app:
            self.routes.append(Mount(path, app=app, name=name))
        elif routes:
            self.routes.append(Mount(path, routes=routes, name=name))
    
    @property
    def model_pattern(self):
        return re.compile(r'({})'.format('|'.join(keymodel.ModelMap.keys())))
    
    @property
    def action_pattern(self):
        return re.compile(r'({})'.format('|'.join(self.ACTIONS)))
    
    @property
    def micro_pattern(self):
        return re.compile(r'({})'.format('|'.join(self.MICROS)))
    
    @staticmethod
    def route_methods(action: str):
        return {
                'update': ['GET', 'POST'],
                'create': ['GET', 'POST'],
            
        }.get(action, ['GET'])
    
    @staticmethod
    async def process_form_data(request: Request):
        return await process_form_data(request)
    
    async def create_endpoint(self, request: Request):
        if result := self.model_pattern.search(request.url.path):
            md: model.ModelType = keymodel.ModelMap[result.group(0)]
            if request.method == 'POST':
                data = await self.process_form_data(request)
                await md.update_context()
                new = md(**data)
                return HTMLResponse(str(new))
            
            elif request.method == 'GET':
                return HTMLResponse(str(form.Form(md, request, action=f'/auto/create/{md.item_name()}')))
        return HTMLResponse(request.url.path)
    
    def create_mount(self):
        return Mount('/create', name='create', routes=[
                Route(f'/{item.item_name()}', self.create_endpoint, name=item.item_name(), methods=['GET', 'POST']) for
                item in keymodel.ModelMap.values()
        ])
    
    def static_mount(self):
        return Mount('/static', name='static', app=self.static)
    
    def auto_mount(self):
        return Mount('/auto', name='auto', routes=[
                self.create_mount()
        ])


def make_endpoint(app: App, model: type[model.ModelType], action: Literal['new', 'detail', 'list']):
    if action == 'new':
        async def endpoint(request: Request):
            if request.method == 'GET':
                return app.templates.TemplateResponse(f'form/{model.item_name()}.jj', {'request': request, 'model': model})
            elif request.method == 'POST':
                data = await process_form_data(request)
                await model.update_context()
                instance: model.ModelType = model(**data)
                exist = await instance.exist()
                if exist:
                    return HTMLResponse(Markup(element.H6(children=f'Este objeto já existe no banco de dados: {instance}')))
                saved = await instance.save()
                if saved:
                    return HTMLResponse(Markup(element.H6(children=f'Objeto criado com sucesso: {saved}')))
                return HTMLResponse(Markup(element.H6(children=f'O objeto não pode ser salvo')))
        return endpoint
    elif action == 'list':
        async def endpoint(request: Request):
            await model.update_context()
            instances = await model.sorted_instances(query={**request.query_params})
            return app.templates.TemplateResponse('list.jj', {'request': request, 'instances': instances})
        return endpoint
    elif action == 'detail':
        async def endpoint(request: Request):
            await model.update_context()
            instance = await model.init_from_db(request.path_params.get('key'))
            return app.templates.TemplateResponse(f'detail/{model.item_name()}.jj', {'request': request, 'instance': instance})
        return endpoint


async def process_form_data(request: Request):
    form_data = await request.form()
    result = defaultdict(list)
    cleaned = {**request.path_params}
    for k, v in form_data.multi_items():
        result[k].append(v)
    for k, v in result.items():
        if len(v) == 0:
            cleaned[k] = None
        elif len(v) == 1:
            cleaned[k] = v[0]
        else:
            cleaned[k] = v
    return cleaned


class RouteNew(Route):
    def __init__(self, model: type[model.ModelType], template_engine: Jinja2Templates, template_path: str = None):
        self.model = model
        self.template_engine = template_engine
        self._template_path = template_path
        super().__init__(f'/new/{self.item_name}', self.endpoint, name=f'new-{self.item_name}', methods=['GET', 'POST'])
        
    @property
    def item_name(self):
        return self.model.item_name()
    
    @property
    def template_path(self):
        return self._template_path or f'/form/{self.item_name}.jj'
    
    @property
    def template(self):
        return self.template_engine.get_template(self.template_path)
        
    async def endpoint(self, request: Request):
        if request.method == 'GET':
            return self.template.render(request=request)
        elif request.method == 'POST':
            data = await process_form_data(request)
            await self.model.update_context()
            instance: model.ModelType = self.model(**data)
            exist = await instance.exist()
            if exist:
                return HTMLResponse(Markup(element.H6(children=f'Este objeto já existe no banco de dados: {instance}')))
            saved = await instance.save()
            if saved:
                return HTMLResponse(Markup(element.H6(children=f'Objeto criado com sucesso: {saved}')))
            return HTMLResponse(Markup(element.H6(children=f'O objeto não pode ser salvo')))

        