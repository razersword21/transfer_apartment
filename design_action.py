from qwen_3b_llm import *
from prompt import *
import json

with open("personal_information\lin\information.json", "r", encoding="utf-8") as f:
    person_information = json.load(f)

daily_schedule, times = make_design(person_information, design_action)

print(daily_schedule)
print("執行時間:", times)