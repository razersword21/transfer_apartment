from transformers import AutoModelForCausalLM, AutoTokenizer
import time

model_name = "Qwen/Qwen2.5-3B-Instruct"

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained(model_name)

person_information = {
    "name":"林志",
    "age":45,
    "job_occupation":"藥房店員",
    "interests":"跑步、做飯",
    "personality":"熱心幫助別人、勤奮、友善",
    "character_description":"林志是Willow Market藥房的店員，熱心助人。他與妻子Mei Lin和兒子Eddy Lin住在一起。John認識他的鄰居Sam和Jennifer Moore，認為他們非常友善。他經常與鄰居Yuriko Yamamoto打招呼，並偶爾與同事Tom討論政治話題。"
}

prompt = """生成你今天的例行行程，行程一定包含起床、吃飯(早、中、晚)、上班或上學、放學或下班、睡覺，行程的順序要合理，以json回傳，回傳範例格式如下
{
    {"time":"07:00", "action":"起床，刷牙、吃早餐"},
    {"time":"08:00", "action":"準備去健身房上班"},
}
最少生成6條行程，最多10條"""

messages = [
    {"role": "system", "content": "<人物資訊>{person_information}</人物資訊>你是一位生活在社區的人，人物資訊參考<人物資訊>，所有行為決定和講話方式都以該人物的視角思考與動作。".format(person_information = str(person_information))},
    {"role": "user", "content": prompt}
]

text = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True
)
model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

start_time = time.time()
generated_ids = model.generate(
    **model_inputs,
    max_new_tokens=512
)
generated_ids = [
    output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
]

response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
print(response)
print(time.time()-start_time)