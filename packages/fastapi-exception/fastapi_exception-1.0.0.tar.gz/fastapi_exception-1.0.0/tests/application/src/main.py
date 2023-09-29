from typing import List, Union

from fastapi import FastAPI
from fastapi_global_variable import GlobalVariable
from pydantic import BaseModel, Field

from fastapi_exception.config import FastApiException
from fastapi_exception.custom_errors.duplicate_error import DuplicateError
from fastapi_exception.utils.throw_validation import throw_validation_field_with_exception

from .config.i18n import i18n_service

app = FastAPI(title="Test App")

GlobalVariable.set('app', app)

FastApiException.config(i18n_service)


class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None
    x: List[int] = Field(min_length=3)
    y: List[int] = Field(max_length=1)


@app.post("/items")
def create_items(item: Item):
    return {"item_name": item.name}


@app.post("/cars")
def create_cars():
    # throw_validation(type='invalid_car_wheel', loc=('body', 'wheel'))
    throw_validation_field_with_exception(DuplicateError('wheel', ('body', 'wheel')).__dict__())
    return True
