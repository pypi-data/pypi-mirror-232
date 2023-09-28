from __future__ import annotations

import json
from contextvars import copy_context, ContextVar
from functools import cache
from typing import Annotated, Any, Callable, ClassVar, Generic, Literal, Optional, overload, Type, TypeVar, Union
from collections import ChainMap, UserString

from markupsafe import Markup
from pydantic import BeforeValidator, computed_field, ConfigDict, BaseModel, Field, field_serializer
from starlette.requests import Request
from typing_extensions import Self

from . import db as db, functions as fn, element as el, metadata as meta



class KeyModel(BaseModel):
    # model config
    model_config = ConfigDict(extra='allow', str_strip_whitespace=True, arbitrary_types_allowed=True)
    # classvars
    ACTIONS: ClassVar[tuple[str]] = ('create', 'update', 'list', 'search', 'detail', 'select-options', 'datalist-options')
    CTXVAR: ClassVar[ContextVar] = None
    EXIST_QUERY: ClassVar[Union[str, list[str]]] = None
    FETCH_QUERY: ClassVar[Union[dict, list[dict]]] = None
    SEARCH_HANDLER: ClassVar[Callable[[Self], str]] = None
    SINGULAR: ClassVar[str] = None
    PLURAL: ClassVar[str] = None
    TABLE: ClassVar[str] = None
    DATALIST_FIELDS: ClassVar[set[str]] = None # used to add data-field attribute to datalist option element
    PROJECT_KEY_NAME: ClassVar[str] = 'DETA_PROJECT_KEY'
    PROJECT: ClassVar[db.DetaProject] = None
    key: Optional[str] = None
        
    def delete_button(self):
        return Markup(el.Element('button', class_names='btn-trash', htmx={
                'confirm': f"Confirma excluir {self.singular().lower()}, chave {self.key}. Esta ação não pode ser desfeita.",
                'post': f'/delete/{self.item_name()}/{self.key}'}, children='<i class="bi bi-trash3"></i>'))

    @classmethod
    def key_fields(cls):
        return [k for k, v in cls.model_fields.items() if v.annotation in [cls.Key, Optional[cls.Key]]]
    
    @classmethod
    def key_field_models(cls):
        result = []
        for item in cls.key_fields():
            if mt:= meta.fullmetadata(cls, item):
                result.extend([get_model(i) for i in mt.tables])
        return fn.filter_uniques(result)
    
    @classmethod
    def table_key_fields(cls):
        return [k for k, v in cls.model_fields.items() if v.annotation in [cls.TableKey, Optional[cls.TableKey]]]
    
    @classmethod
    def table_key_field_models(cls):
        result = []
        for item in cls.table_key_fields():
            if mt:= meta.fullmetadata(cls, item):
                result.extend([get_model(i) for i in mt.tables])
        return fn.filter_uniques(result)
    
    @classmethod
    def singular(cls):
        return cls.SINGULAR or cls.__name__
    
    @classmethod
    def plural(cls):
        return cls.PLURAL or f'{cls.singular()}s'
    
    @classmethod
    def table(cls)-> str:
        return cls.TABLE or cls.classname()
    
    @classmethod
    def datalist_fields(cls):
        return cls.DATALIST_FIELDS or {}
    
    @classmethod
    def classname(cls):
        return cls.__name__
    
    def __lt__(self, other):
        return fn.normalize_lower(str(self)) < fn.normalize_lower(str(other))
    
    class TableKey(UserString):
        def __init__(self, v: str):
            if v:
                val = v.split()[0]
                if not '.' in val:
                    raise ValueError('TableKey exige valor com os nomes de tabela e chave (Table.key)')
                self.table, self.value = val.split('.')
                super().__init__(f'{self.table}.{self.value}')
            else:
                super().__init__('')
    
    class Key(UserString):
        def __init__(self, v: str):
            if v:
                val = v.split()[0]
                if '.' in val:
                    self.table, self.value = val.split('.')
                else:
                    self.table, self.value = None, val
                super().__init__(val)
            else:
                super().__init__('')
                
    @classmethod
    def key_name(cls):
        return f'{cls.item_name()}_key'

    @computed_field(repr=False)
    @property
    def search(self) -> str:
        if self.SEARCH_HANDLER:
            return self.SEARCH_HANDLER()
        return fn.normalize_lower(str(self))
        
    @classmethod
    def item_name(cls):
        return fn.cls_name_to_slug(cls.__name__)
    
    @field_serializer('key')
    def key_serializer(self, v: str | None, _info):
        if v:
            return v
        return None
    
    @classmethod
    async def fetch_all(cls, query: dict | list[dict] | None = None):
        return await cls.PROJECT.fetch_all(cls.table(), query=query)
    
    @classmethod
    async def fetch_one(cls, key: str) -> Optional[dict]:
        return await cls.PROJECT.fetch_one(cls.table(), key)
    
    @classmethod
    async def fetch(cls, query: dict | list[dict] | None = None, last: str | None = None):
        return await cls.PROJECT.fetch(cls.table(), query=query, last=last)
    
    @classmethod
    async def create_key(cls, key: str = None):
        return await cls.PROJECT.create_key(cls.table(), key=key)

    def exist_query(self):
        asjson = self.asjson()
        
        if isinstance(self.EXIST_QUERY, list):
            query = []
            for item in self.EXIST_QUERY:
                query.append({k: asjson.get(k) for k in item.split() if k})
        else:
            query = {k: asjson.get(k) for k in self.EXIST_QUERY.split() if k}
            
        return query
    
    
    async def exist(self) -> Optional[dict]:
        result = await self.fetch(self.exist_query())
        if result.count == 1:
            return result.items[0]
        elif result.count == 0:
            return None
        else:
            raise db.DatabaseException('a pesquisa "exist" retornou mais de uma possibilidade')

    def asjson(self, **kwargs):
        return json.loads(self.model_dump_json(**kwargs))
    
    @classmethod
    @cache
    def dependants(cls):
        
        result = list()
        
        def recursive(model: type[KeyModelType]):
            result.append(model)
            if dependants := model.primary_dependants():
                for item in dependants:
                    recursive(item)
        
        for md in cls.primary_dependants():
            recursive(md)
        
        return fn.filter_uniques(result)
    
    
    @classmethod
    @cache
    def primary_dependants(cls):
        return fn.filter_not_none(fn.filter_uniques([*cls.key_field_models(), *cls.table_key_field_models()]))

    @classmethod
    @cache
    def dependant_fields(cls):
        return fn.filter_not_none([*cls.key_fields(), *cls.table_key_field()])
    
    @classmethod
    @cache
    def instance_property_name(cls, name: str):
        mt = meta.fullmetadata(cls, name)
        return mt.item_name or name.replace('_key', '')

KeyModelType = TypeVar('KeyModelType', bound=KeyModel)


ModelMap: ChainMap[str, type[KeyModelType]] = ChainMap()



@overload
def get_model(value: str) -> type[KeyModelType]:
    ...

@overload
def get_model(value: Request) -> type[KeyModelType]:
    ...


def get_model(value: Request | str) -> Optional[type[KeyModelType]]:
    if isinstance(value, str):
        if value[0].isupper():
            return ModelMap.get(fn.cls_name_to_slug(value), None)
        else:
            value = value.replace('_key', '')
            return ModelMap.get(value, None)
    elif isinstance(value, Request):
        return ModelMap[value.path_params.get('item_name', value.path_params.get('model'))]
    else:
        return None

