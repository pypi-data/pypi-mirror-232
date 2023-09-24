from typing import TypeVar, Generic

from pydantic.generics import GenericModel

T = TypeVar('T')
D = TypeVar('D')


class RestfulResponse(GenericModel, Generic[T]):
    code: int = 200
    msg: str = 'success'
    data: T


class RestfulPageResponse(GenericModel, Generic[D]):
    code: int = 200
    message: str = 'success'
    page: int = 1
    total: int = 0
    data: D
