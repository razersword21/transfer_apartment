from qwen_3b_llm import *
from prompt import *
from process_method import *
import json


with open("personal_information\wang\information.json", "r", encoding="utf-8") as f:
    person_information = json.load(f)

check_json_format_flag = False

while(check_json_format_flag == False):
    daily_schedule, times = make_design(person_information['background'], daily_routine)
    print("生成結果: {}".format(daily_schedule))
    daily_schedule, check_json_format_flag = check_json_format(daily_schedule, check_json_format_flag)
    print("檢查狀態: {}".format(check_json_format_flag))

person_information['schedule'] = daily_schedule['today_schedule']
with open("personal_information\wang\information.json", "w", encoding="utf-8") as f:
    json.dump(person_information, f, ensure_ascii=False, indent=1)

print("執行時間:", times)