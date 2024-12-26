from model import *
from prompt_new import *
from method import *
from config_new import *
import copy
import json
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

# import intel_npu_acceleration_library

MODEL = AutoModelForCausalLM.from_pretrained(
    model_name,
    use_cache=True
).eval()
# print("Compile model for the NPU")
# MODEL = torch.compile(MODEL, backend="npu")
TOKENIZER = AutoTokenizer.from_pretrained(model_name, use_default_system_prompt=False)

def schedule_create(person_information, todaytime):
    check_json_format_flag = False
    daily_prompt = daily_routine.format(memory=person_information['memory'], current_time=todaytime)+daily_routine_prompt

    while(check_json_format_flag == False):
        daily_schedule, times = make_design(MODEL, TOKENIZER, person_information['personality'], daily_prompt)
        print("行程表: {}".format(daily_schedule))
        daily_schedule, check_json_format_flag = check_json_format(daily_schedule, check_json_format_flag)

    return daily_schedule

def schedule_create_method(personality, person_memory, todaytime):
    check_json_format_flag = False
    daily_prompt = daily_routine.format(memory=person_memory, current_time=todaytime)+daily_routine_prompt

    while(check_json_format_flag == False):
        daily_schedule, times = make_design(MODEL, TOKENIZER, personality, daily_prompt)
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
    return action["action"]

def design_action_method(personality, memory, temp_memory, schedule, observe, current_location, current_time, location_list, all_location_object, nearby_characters):
    check_json_format_flag = False
    nearby_people = copy.deepcopy(nearby_characters)
    nearby_people.remove(personality["name"])

    action_prompt = design_action.format(memory=memory, 
                         temp_memory=temp_memory,
                         schedule=schedule, 
                         observes=observe, 
                         current_location=current_location, 
                         current_time=current_time,
                         location_list=location_list,
                         all_location_object=all_location_object,
                         nearby_people=nearby_people)+design_action_prompt
    
    device = next(MODEL.parameters()).device
    print(f"模型所在設備: {device}")
    while(check_json_format_flag == False):
        action, times = make_design(MODEL, TOKENIZER, personality, action_prompt)
        print("動作: {}".format(action))
        action, check_json_format_flag = check_json_format(action, check_json_format_flag)

    # print("執行時間:", times)
    return action

def check_additional_action_method(personality, memory, schedule, observe, current_location, current_time, nearby_characters):
    check_json_format_flag = False
    nearby_people = copy.deepcopy(nearby_characters)
    nearby_people.remove(personality["name"])

    additional_action_prompt = check_addition_action.format(memory=memory, 
                         schedule=schedule, 
                         observes=observe, 
                         current_location=current_location, 
                         current_time=current_time, 
                         nearby_people=nearby_people)+check_addition_action_prompt
    while(check_json_format_flag == False):
        additional_action, times = make_design(MODEL, TOKENIZER, personality, additional_action_prompt)
        print("額外動作: {}".format(additional_action))
        additional_action, check_json_format_flag = check_json_format(additional_action, check_json_format_flag)
    # print("執行時間:", times)
    return additional_action

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

def thinking_method(memory, observe, current_location, current_time):
    check_json_format_flag = False
    think_prompt = create_thought.format(memory=memory,
                         observes=observe,
                         current_location=current_location,
                         current_time=current_time)+create_thought_prompt

    while(check_json_format_flag == False):
        think, times = make_design(MODEL, TOKENIZER, personality, think_prompt)
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

def check_need_adjust_schedule_method(memory, schedule, observe, current_time):
    check_json_format_flag = False
    check_need_adjust_prompt = check_adjust.format(memory=memory,
                         schedule=schedule,
                         observes=observe,
                         current_time=current_time)+check_adjust_prompt

    while(check_json_format_flag == False):
        check_need_adjust, times = make_design(MODEL, TOKENIZER, personality, check_need_adjust_prompt)
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

def adjsut_schedule_method(memory, schedule, observe, current_time):
    check_json_format_flag = False
    adjsut_schedule_prompt = adjust_routine.format(memory=memory,
                         schedule=schedule,
                         observes=observe,
                         current_time=current_time)+adjust_routine_prompt
    while(check_json_format_flag == False):
        adjsuted_schedule, times = make_design(MODEL, TOKENIZER, personality, adjsut_schedule_prompt)
        print("修改行程表: {}".format(adjsuted_schedule))
        adjsuted_schedule, check_json_format_flag = check_json_format(adjsuted_schedule, check_json_format_flag)
    print("執行時間:", times)
    return adjsuted_schedule["adjust_schedule"]

def create_dialogue_method(personality, interactive_character, memory,  observe, current_location, current_time, dialogue_history):
    check_json_format_flag = False
    dialogue_prompt = create_dialogue.format(interactive_character=interactive_character,
                         memory=memory,
                         observes=observe,
                         current_location=current_location,
                         current_time=current_time,
                         dialogue_history=dialogue_history)+create_dialogue_prompt
    while(check_json_format_flag == False):
        dialogue, times = make_design(MODEL, TOKENIZER, personality, dialogue_prompt)
        print("對話: {}".format(dialogue))
        dialogue, check_json_format_flag = check_json_format(dialogue, check_json_format_flag)
    print("執行時間:", times)
    return dialogue["dialogue"]

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