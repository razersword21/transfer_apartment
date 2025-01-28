import os
from fastapi import APIRouter, Response, status, Request, HTTPException
from asyncio import get_event_loop, Lock
import concurrent.futures
from toolkit.lib import *
from toolkit.method import *
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import re

if __name__ == 'routers.classifier_v1':
    TAG_MODEL_VERSION = 'v1'
    router = APIRouter(prefix='/v1/design_model', tags=[TAG_MODEL_VERSION])
    lock = Lock()
    EXECUTOR = concurrent.futures.ThreadPoolExecutor()
    model_name = "Qwen/Qwen2.5-3B-Instruct"
    MODEL = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",
        device_map="auto"
    ).eval()
    print(torch.cuda.is_available())
    print(MODEL.device)
    TOKENIZER = AutoTokenizer.from_pretrained(model_name, use_default_system_prompt=False)
    SYSTEM_PROMPT = """<人物資訊>{person_information}</人物資訊>你是一位人物角色，人物背景資料參考"人物資訊"，根據該人物的"人物資訊"決定所有想法、行為和講話方式。"""

# @router.on_event("startup")
# async def startup():
#     pass

@router.post('/make_design', responses={
    200: {'model': Response},
    400: {'model': HTTPErrorResult},
    500: {'model': HTTPErrorResult},
})
@catch_error
async def make_design_endp(request: Request):
    event_loop = get_event_loop()
    async with lock:
        generate_result = await event_loop.run_in_executor(None, make_design, MODEL, TOKENIZER, request.person_information, request.prompt, SYSTEM_PROMPT)
    return Response(generate_dict=generate_result)

@router.post('/transfer_model', responses={
    200: {'model': transfer_response},
    400: {'model': HTTPErrorResult},
    500: {'model': HTTPErrorResult},
})
@catch_error
async def transfer_model_endp(request: transfer_request):
    event_loop = get_event_loop()
    async with lock:
        generate_result = await event_loop.run_in_executor(None, transfer_model, MODEL, TOKENIZER, request.prompt)
    return transfer_response(generate_text=generate_result)