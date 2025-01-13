from __future__ import annotations
import logging
from dataclasses import dataclass
from pydantic_settings import BaseSettings
from functools import wraps
from typing import Any, Callable, Coroutine, Optional
from typing_extensions import ParamSpec
from fastapi.responses import JSONResponse

from pydantic import BaseModel 

class Request(BaseModel):
    person_information: dict
    prompt: str

class Response(BaseModel):
    generate_dict: dict

@dataclass
class Errors:
    NO_INPUT_ERROR = JSONResponse({'result':3}, 400)
    INTERNAL_ERROR = JSONResponse({'result':999}, 500)


logger = logging.getLogger('uvicorn.error')
P = ParamSpec('P')

def catch_error(func: Callable[P, Coroutine[Any, Any, Any]]) -> Callable[P, Coroutine[Any, Any, Any]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as ex:
            logger.error(str(ex), exc_info=True, stack_info=True)
            return Errors.INTERNAL_ERROR

    return wrapper