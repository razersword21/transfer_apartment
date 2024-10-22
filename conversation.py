from qwen_3b_llm import *
from prompt import *
import json

with open("personal_information\origin_information\p1_information.json", "r", encoding="utf-8") as f:
    person_information = json.load(f)

daily_schedule, times = make_design(person_information, create_dialogue)

print(daily_schedule)
print("執行時間:", times)