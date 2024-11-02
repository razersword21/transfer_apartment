from transformers import AutoModelForCausalLM, AutoTokenizer
from qwen_3b_llm import *
import json
from planning_prompt import *
from datetime import datetime

with open("personal_information\lin\information.json", "r", encoding="utf-8") as f:
    person_information = json.load(f)



if __name__ == "__main__":
    # 設定大概日程
    broad_plan, _ = make_design(person_information, daily_routine)
    
    daily_routine_hourly.format(broad_plan)
    # 生成每小時任務的細節
    hourly_plan, _ = make_design(person_information, daily_routine_hourly)
    
    # 遞歸細分為 5 到 15 分鐘的小步驟
    detailed_plan, _ = make_design(person_information, daily_routine_MIN)
    
    # 輸出最終計劃
    print("大致日程:")
    print(broad_plan)
    print("\n每小時計劃:")
    print(hourly_plan)
    print("\n細分的行為計劃:")
    print(detailed_plan)