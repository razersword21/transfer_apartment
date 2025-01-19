import logging
logging.basicConfig(level=logging.INFO)
import time

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
    logging.info(f"\n生成:\n{response}\n生成時間: {time.time()-start_time}")
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