from qwen_3b_llm import *
from prompt import *
import json

with open("personal_information\lin\information.json", "r", encoding="utf-8") as f:
    person_information = json.load(f)
design_action.format(action_history=person_information['action_history'], memory=person_information['memory'], schedule=person_information['schedule'], observes=..., current_location=..., current_time=...)
daily_schedule, times = make_design(person_information, design_action)

print(daily_schedule)
print("執行時間:", times)