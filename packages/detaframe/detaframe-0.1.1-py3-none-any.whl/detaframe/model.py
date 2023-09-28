from __future__ import annotations

from collections import ChainMap
from contextvars import ContextVar, copy_context
from functools import cache, wraps
from typing import Any, Optional, overload, TypeVar

from markupsafe import Markup
from typing_extensions import Self

from . import keymodel, db, element, ctx


ModelMap: ChainMap[str, ModelType] = keymodel.ModelMap


class Model(keymodel.KeyModel):
    
    def model_post_init(self, __context: Any) -> None:
        super().model_post_init(__context)
        for key_name in self.dependant_fields():
            key = getattr(self, key_name)
            item_name = self.instance_property_name(key_name)
            print(item_name)
            if key:
                if '.' in key:
                    model_name, key_value = key.split('.')
                    model = keymodel.get_model(model_name)
                    setattr(self, item_name, ctx.instance_from_context(model, key_value))
                else:
                    setattr(self, item_name, ctx.instance_from_context(item_name, key))
            else:
                setattr(self, item_name, None)
    
    @classmethod
    def project(cls):
        return cls.PROJECT
    
    @classmethod
    async def initiate(cls, *args, **kwargs) -> Self:
        result = None
        try:
            result = cls(*args, **kwargs)
        except:
            await cls.update_context()
            result = cls(*args, **kwargs)
        finally:
            return result
        
    @classmethod
    async def update_context(cls, lazy: bool = False):
        await ctx.populate_context(cls.dependants(), lazy=lazy)
        
    @classmethod
    async def instances(cls, query: list[dict] | dict | None = None, lazy: bool = False):
        await cls.update_context(lazy=lazy)
        return [cls(**i) for i in await cls.fetch_all(query)]
    
    @classmethod
    async def sorted_instances(cls, query: list[dict] | dict | None = None, lazy: bool = False):
        return sorted(await cls.instances(query=query, lazy=lazy))
    
    @classmethod
    async def init_from_db(cls, key: str) -> Self:
        result = None
        data = await cls.fetch_one(key)
        try:
            result = cls(**data)
        except:
            await cls.update_context(lazy=True)
            result = cls(**data)
        finally:
            return result
        
        
    async def save_new(self, **kwargs):
        await self.update_context(lazy=True)
        if exist:= await self.exist():
            return type(self)(**exist)
        else:
            return await self.save(**kwargs)
        
    async def save(self, **kwargs):
        await self.update_context(lazy=True)
        saved = await self.PROJECT.save(self.table(), self.asjson(**kwargs))
        if saved:
            return type(self)(**saved)
        return None
    
    async def update(self, **kwargs):
        if self.key:
            saved = await self.PROJECT.save(self.table(), self.asjson(**kwargs))
            if saved:
                return await self.initiate(**saved)
            return None
        raise Exception('Apenas instâncias com "key" pode ser atualizadas.')
        
    @property
    def table_key(self):
        return f'{self.table()}.{self.key}'
    
    def html_option(self):
        return Markup(element.Element('option', value=self.table_key, children=str(self), id=self.table_key))
    
    def key_with_str(self):
        return f'{self.key} | {self}'
    

    
ModelType = TypeVar('ModelType', bound=Model)


def model_map(cls: type[Model]):
    @wraps(cls)
    def wrapper():
        assert cls.EXIST_QUERY, 'cadastrar "EXIST_QUERY" na classe "{}"'.format(cls.__name__)
        keymodel.ModelMap[cls.item_name()]: cls = cls
        cls.CTXVAR = ContextVar(f'{cls.__name__}Var', default=dict())
        cls.PROJECT = db.DetaProject(cls.PROJECT_KEY_NAME)
        return cls
    return wrapper()

