from qwen_3b_llm import *
from prompt import *
from process_method import *
import json

with open("personal_information\origin_information\p1_information.json", "r", encoding="utf-8") as f:
    person_information = json.load(f)

check_json_format_flag = False
current_data = {
    "location": "藥房",
    "time": time.time()
}

design_action.format(action_history=person_information['action_history'], memory=person_information['memory'], schedule=person_information['schedule'], observes=[], current_location=current_data["location"], current_time=current_data["time"])
while(check_json_format_flag == False):
    action, times = make_design(person_information, design_action+design_action_prompt)
    print("生成結果: {}".format(action))
    action, check_json_format_flag = check_json_format(action, check_json_format_flag)
    print("檢查狀態: {}".format(check_json_format_flag))

print(action)
print("執行時間:", times)