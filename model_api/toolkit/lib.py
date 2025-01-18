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
    person_information: dict = {
        "name": "陳宇翔",
        "age": 18,
        "job_occupation": "學生",
        "interests": "閱讀、音樂、冥想",
        "personality": "內向、心思細膩、樂於傾聽",
        "character_description": "陳宇翔是一位剛入學的瓦羅蘭大學新生，剛搬入宿舍，喜歡在空閒時間閱讀和聆聽音樂。雖然性格偏內向，但他非常善於傾聽和理解別人，讓人容易信任。冥想讓他保持平靜，他期待著能認識一些志同道合的朋友，並對大學生活充滿了好奇和期待。"
    }
    prompt: str = "生成你現在的想法"

class Response(BaseModel):
    generate_dict: str #dict

class HTTPErrorResult(BaseModel):
    result: int

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