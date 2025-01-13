import os
from fastapi import APIRouter, Response, status, Request, HTTPException
from asyncio import get_event_loop, Lock
import concurrent.futures
from toolkit.lib import *
from transformers import AutoModelForCausalLM, AutoTokenizer

if __name__ == 'routers.classifier_v1':
    TAG_MODEL_VERSION = 'v1'
    router = APIRouter(prefix='/v1/design_model', tags=[TAG_MODEL_VERSION])
    lock = Lock()
    EXECUTOR = concurrent.futures.ThreadPoolExecutor()

@router.on_event("startup")
async def startup():

    MODEL = AutoModelForCausalLM.from_pretrained(
        model_name,
        use_cache=True
    ).eval()
    TOKENIZER = AutoTokenizer.from_pretrained(model_name, use_default_system_prompt=False)
    SYSTEM_PROMPT = """<人物資訊>{person_information}</人物資訊>你是一位人物角色，人物背景資料參考"人物資訊"，根據該人物的"人物資訊"決定所有想法、行為和講話方式。"""

@router.post('/make_design', responses={
    200: {'model': Response},
    400: {'model': HTTPErrorResult},
    500: {'model': HTTPErrorResult},
})
@catch_error
async def make_design(Request: request):
    event_loop = get_event_loop()
    async with lock:
        generate_result = await event_loop.run_in_executor(None, make_design, MODEL, TOKENIZER, request.person_information, request.prompt, SYSTEM_PROMPT)
    return Response(generate_dict=generate_result)

