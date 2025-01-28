import logging
logging.basicConfig(level=logging.INFO)
import time
import json
import re

def make_design(model, tokenizer, person_information: dict, prompt: str, SYSTEM_PROMPT: str):
    logging.info(f"\nmake_design 輸入:\n{person_information}\n提示詞: {prompt}")
    start_time = time.time()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT.format(person_information = str(person_information))},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print_colored(f"\n生成:\n{response}\n生成時間: {time.time()-start_time}", '黃色')
    return response

def transfer_model(model, tokenizer, prompt: str):
    messages = [
        {"role": "user", "content": prompt}
    ]
    logging.info(f"\ntransfer_model 輸入:\n{prompt}")
    start_time = time.time()

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    generated_ids = model.generate(
        **model_inputs,
        max_new_tokens=1024
    )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    logging.info(f"\n生成:\n{response}\n生成時間: {time.time()-start_time}")
    return response

def check_json_format(data: str, flag: bool):
    try:
        result = json.loads(data)
        flag = True
    except json.JSONDecodeError:
        try:
            json_string = re.search(r"```json(.*)```", data, re.DOTALL).group(1).strip()
            result = json.loads(json_string)
            flag = True
        except (json.JSONDecodeError, AttributeError):
            result = None
    return result, flag

# debug 用
import sys
def print_colored(text, color, end='\n'):
    colors = {
        '紅色': '\x1b[31m',
        '綠色': '\x1b[32m',
        '黃色': '\x1b[33m',
        '藍色': '\x1b[34m',
        '紫色': '\x1b[35m',
        '青色': '\x1b[36m'
    }
    reset = '\x1b[0m'
    sys.stdout.write(colors.get(color, '') + text + reset + end)