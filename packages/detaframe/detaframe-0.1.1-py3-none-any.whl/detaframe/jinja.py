from __future__ import annotations

import os

from markupsafe import Markup
from starlette.templating import Jinja2Templates

from . import db as db, keymodel as bm, form as fm, element, functions, model

templates = Jinja2Templates(directory=os.path.join(os.getcwd(), 'templates'))
templates.env.globals['config'] = db.config
templates.env.globals['str'] = str
templates.env.globals['get_model'] = bm.get_model
templates.env.globals['Form'] = fm.Form
templates.env.globals['ffield'] = fm.BasicFormField
templates.env.globals['lang'] = db.config.get("HTML_LANG", default='en')
templates.env.globals['element'] = element.Element
templates.env.globals['Markup'] = Markup
templates.env.globals['today'] = functions.today
templates.env.globals['today_iso'] = lambda : functions.today().isoformat()
templates.env.globals['now_iso'] = functions.now_iso
templates.env.globals['random_id'] = functions.random_id


def list_template(model: type[model.ModelType]):
    temp = templates.get_template('list/index.jj')
    try:
        temp = templates.get_template(f'list/{model.item_name()}.jj')
    finally:
        return temp
    
def form_template(model: type[model.ModelType]):
    temp = templates.get_template('form/index.jj')
    try:
        temp = templates.get_template(f'form/{model.item_name()}.jj')
    finally:
        return temp
    
def detail_template(model: type[model.ModelType]):
    temp = templates.get_template('detail/index.jj')
    try:
        temp = templates.get_template(f'detail/{model.item_name()}.jj')
    finally:
        return temp

class Render:
    
    @staticmethod
    def list_item(instance: model.ModelType, **kwargs):
        return element.Li(class_names='list-item',children=str(instance), **kwargs)
    
    @staticmethod
    def list_anchor(instance: model.ModelType, **kwargs):
        return element.A(class_names='list-anchor',children=str(instance), href=f'/get/detail/{instance.item_name()}/{instance.key}', **kwargs)
    
    @staticmethod
    def anchor(**kwargs):
        return element.A(**kwargs)
    
    @staticmethod
    def list_item_anchor(instance: model.ModelType, **kwargs):
        return element.Li(class_names='list-item', children=Render.list_anchor(instance), **kwargs)
    
    @staticmethod
    def list_group(instances: list[model.ModelType], **kwargs):
        return element.Ul(class_names='list-group', children=[Render.list_item(item) for item in instances], **kwargs)
    
    @staticmethod
    def list_group_title(model: type[model.ModelType], **kwargs):
        return element.H3(children=f'Lista de {model.plural()}', class_names='list-group-title', **kwargs)
    
    @staticmethod
    def htmx_title(children: str | element.Element | list[element.Element], **kwargs):
        return element.Div(id='htmx-title', children=children, **kwargs)
    
    @staticmethod
    def htmx_content(children: str | element.Element | list[element.Element], **kwargs):
        return element.Div(id='htmx-content', children=children, **kwargs)
    
    @staticmethod
    def htmx_container(children: str | element.Element, **kwargs):
        return element.Div(id='htmx-container', children=children, **kwargs)
    
    @staticmethod
    def htmx_container_link(path: str, children: str | element.Element, **kwargs):
        return element.Span(id='htmx-link', children=children, htmx={'get': path, 'target': '#htmx-container'}, **kwargs)
    
    @staticmethod
    def htmx_content_link(path: str, children: str | element.Element, **kwargs):
        return element.Span(id='htmx-link', children=children, htmx={'get': path, 'target': '#htmx-content'}, **kwargs)


    
templates.env.globals['Render'] = Render