from model import *
from prompt_new import *
from method import *
from config_new import *
from action_method import *
import copy

from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto", 
    device_map="auto"
)
TOKENIZER = AutoTokenizer.from_pretrained(model_name)

def schedule_create(person_information, todaytime):
    check_json_format_flag = False
    daily_prompt = daily_routine.format(memory=person_information['memory'], current_time=todaytime)+daily_routine_prompt

    while(check_json_format_flag == False):
        daily_schedule, times = make_design(MODEL, TOKENIZER, person_information['personality'], daily_prompt)
        print("行程表: {}".format(daily_schedule))
        daily_schedule, check_json_format_flag = check_json_format(daily_schedule, check_json_format_flag)

    return daily_schedule

# 動作決定
def action_design(person_information, current_time, observe, all_location_object, location_list, nearby_characters, temp_memory):
    check_json_format_flag = False
    action_prompt = design_action.format(memory=person_information['memory'], 
                         temp_memory=temp_memory,
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_location=person_information["current_location"], 
                         current_time=current_time,
                         location_list=location_list,
                         all_location_object=all_location_object,
                         nearby_people=nearby_characters)+design_action_prompt
    
    while(check_json_format_flag == False):
        action, times = make_design(MODEL, TOKENIZER, person_information['personality'], action_prompt)
        print("動作: {}".format(action))
        action, check_json_format_flag = check_json_format(action, check_json_format_flag)
    # print("執行時間:", times)
    return action

# 生成想法
def thinking(person_information, observe, current_time):
    check_json_format_flag = False
    think_prompt = create_thought.format(memory=person_information['memory'],
                         observes=observe,
                         current_location=person_information["current_location"],
                         current_time=current_time)+create_thought_prompt
    
    while(check_json_format_flag == False):
        think, times = make_design(MODEL, TOKENIZER, person_information['personality'], think_prompt)
        print("想法: {}".format(think))
        think, check_json_format_flag = check_json_format(think, check_json_format_flag)

    print("執行時間:", times)
    return think["thought"]

# 判斷是否要調行程表
def check_need_adjust_schedule(person_information, observe, current_time):
    check_json_format_flag = False
    check_need_adjust_prompt = check_adjust.format(memory=person_information['memory'], 
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_time=current_time)+check_adjust_prompt
    
    while(check_json_format_flag == False):
        check_need_adjust, times = make_design(MODEL, TOKENIZER, person_information['personality'], check_need_adjust_prompt)
        print("判斷是否要調行程表: {}".format(check_need_adjust.lower()))
        check_need_adjust, check_json_format_flag = check_json_format(check_need_adjust.lower(), check_json_format_flag)

    print("執行時間:", times)
    return check_need_adjust["need_adjust"]

# 修正行程表
def adjsut_schedule(person_information, observe, current_time):
    check_json_format_flag = False
    adjsut_schedule_prompt = adjust_routine.format(memory=person_information['memory'], 
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_time=current_time)+adjust_routine_prompt
    
    while(check_json_format_flag == False):
        adjsuted_schedule, times = make_design(MODEL, TOKENIZER, person_information['personality'], adjsut_schedule_prompt)
        print("修改行程表: {}".format(adjsuted_schedule))
        adjsuted_schedule, check_json_format_flag = check_json_format(adjsuted_schedule, check_json_format_flag)

    print("執行時間:", times)
    return adjsuted_schedule["adjust_schedule"]

def person_reflection(person_information):
    check_json_format_flag = False
    person_reflection_prompt = reflection.format(person_info=person_information['personality'], 
                                                 memory=person_information['memory'])+reflection_prompt
    while(check_json_format_flag == False):
        person_reflection_info, times = make_design(MODEL, TOKENIZER, person_information['personality'], person_reflection_prompt)
        print("反思人物資料: {}".format(person_reflection_info))
        person_reflection_info, check_json_format_flag = check_json_format(person_reflection_info, check_json_format_flag)

    print("執行時間:", times)
    return person_reflection_info