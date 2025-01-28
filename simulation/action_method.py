from model import *
from prompt_new import *
from method import *
from config_new import *
import copy
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging
logging.basicConfig(level=logging.INFO)

# import intel_npu_acceleration_library

# MODEL = AutoModelForCausalLM.from_pretrained(
#     model_name,
#     use_cache=True
# ).eval()
# # print("Compile model for the NPU")
# # MODEL = torch.compile(MODEL, backend="npu")
# TOKENIZER = AutoTokenizer.from_pretrained(model_name, use_default_system_prompt=False)
MODEL = ""
TOKENIZER = ""

# simulation_test
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
    daily_prompt = daily_routine.format(memory=person_memory, 
                                        current_time=todaytime)+daily_routine_prompt
    required_fields = ["today_schedule"]
    daily_schedule = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, daily_prompt, required_fields)

    return daily_schedule

# simulation_test
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
    required_fields = ["action", "location", "object"]
    action = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, action_prompt, required_fields)
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
    required_fields = ["addtion", "person"]
    additional_action = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, additional_action_prompt, required_fields)
    return additional_action

def reaction_method(personality, memory, schedule, observe, current_location, current_time, location_list, all_location_object, nearby_characters, event_content):
    check_json_format_flag = False
    nearby_people = copy.deepcopy(nearby_characters)
    nearby_people.remove(personality["name"])

    reaction_prompt = design_reaction.format(memory=memory,
                         schedule=schedule, 
                         observes=observe, 
                         current_location=current_location, 
                         current_time=current_time,
                         location_list=location_list,
                         all_location_object=all_location_object,
                         nearby_people=nearby_people,
                         event_content=event_content)+design_reaction_prompt
    reqired_fields = ["reaction"]
    reaction = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, reaction_prompt, reqired_fields)
    return reaction

# simulation_test
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

def thinking_method(personality, memory, observe, current_location, current_time):
    check_json_format_flag = False
    think_prompt = create_thought.format(memory=memory,
                         observes=observe,
                         current_location=current_location,
                         current_time=current_time)+create_thought_prompt
    reqired_fields = ["thought"]
    think = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, think_prompt, reqired_fields)
    return think["thought"]

# simulation_test
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

def check_need_adjust_schedule_method(personality, memory, schedule, observe, current_time):
    check_json_format_flag = False
    check_need_adjust_prompt = check_adjust.format(memory=memory,
                         schedule=schedule,
                         observes=observe,
                         current_time=current_time)+check_adjust_prompt
    required_fields = ["need_adjust"]
    check_need_adjust = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, check_need_adjust_prompt, required_fields)
    return check_need_adjust["need_adjust"]

# simulation_test
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

def adjust_schedule_method(personality, memory, schedule, observe, current_time):
    check_json_format_flag = False
    adjsut_schedule_prompt = adjust_routine.format(memory=memory,
                         schedule=schedule,
                         observes=observe,
                         current_time=current_time)+adjust_routine_prompt
    required_fields = ["adjust_schedule"]
    adjsuted_schedule = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, adjsut_schedule_prompt, required_fields)
    return adjsuted_schedule["adjust_schedule"]

def create_dialogue_method(personality, interactive_character, memory,  observe, current_location, current_time, dialogue_history):
    check_json_format_flag = False
    dialogue_prompt = create_dialogue.format(interactive_character=interactive_character,
                         memory=memory,
                         observes=observe,
                         current_location=current_location,
                         current_time=current_time,
                         dialogue_history=dialogue_history)+create_dialogue_prompt
    required_fields = ["dialogue"]
    dialogue = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, dialogue_prompt, required_fields)
    return dialogue["dialogue"]

# simulation_test
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

def personality_reflection_method(personality, memory):
    check_json_format_flag = False
    personality_reflection_prompt = reflection.format(person_info=personality,
                                                       memory=memory)+reflection_prompt
    required_fields = ["job_occupation", "interests", "personality", "character_description"]
    personality_reflection_info = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, personality_reflection_prompt, required_fields)
    return personality_reflection_info

def character_relation_thinking_method(personality, relation_person_name, origin_realationship, memory):
    check_json_format_flag = False
    character_relation_thinking_prompt = relation_think.format(person_name=relation_person_name,
                                                                origin_relationship=origin_realationship,
                                                                memory=memory)+relation_think_prompt
    required_fields = ["relation"]
    character_relation_thinking_info = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, character_relation_thinking_prompt, required_fields)
    return character_relation_thinking_info['relation']

def while_loop_method(check_json_format_flag, model, tokenizer, personality, prompt, required_fields):
    error_count = 0
    while(check_json_format_flag == False):
        # result, times = make_design(model, tokenizer, personality, prompt)
        result = make_design_api(personality, prompt)
        logging.warning(f"生成結果: {result} , {check_json_format_flag}")
        result, check_json_format_flag = check_json_format(result, check_json_format_flag)
        logging.debug(f"生成結果: {result} , {required_fields} , {check_json_format_flag}")
        check_json_format_flag = check_json_output(result, required_fields)
        if check_json_format_flag == False:
            error_count += 1
            logging.warning("輸出格式錯誤，重新生成 {} 次".format(error_count))

    return result