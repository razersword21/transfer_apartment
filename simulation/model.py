from prompt_new import *
from config_new import *
import time
import requests
from threading import Lock

# 建立全域鎖
lock = Lock()

def make_design(model, tokenizer, person_information: dict, prompt: str):
    messages = [
        {"role": "system", "content": person_system.format(person_information = str(person_information))},
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    start_time = time.time()
    with lock:
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=1024
        )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response, time.time()-start_time

def transfer_model(model, tokenizer, prompt: str):
    # post model api
    messages = [
        {"role": "user", "content": prompt}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

    start_time = time.time()
    with lock:
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=1024
        )
    generated_ids = [
        output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]

    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response, time.time()-start_time

def make_design_api(person_information: dict, prompt: str):
    body = {
        "person_information": person_information,
        "prompt": prompt
    }
    response = requests.post(
        local_api_url+"/make_design", json=body, verify=False
    )
    return response.json()['generate_dict']

def transfer_model_api(prompt: str):
    body = {
        "prompt": prompt
    }
    response = requests.post(
        local_api_url+"/transfer_model", json=body, verify=False
    )
    return response.json()['generate_text']