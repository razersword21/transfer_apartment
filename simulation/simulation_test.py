from model import *
from prompt_new import *
from method import *
from config_new import *


from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
TOKENIZER = AutoTokenizer.from_pretrained(model_name)


# 行程表生成
def daily_routine_create(path: str, todaytime: str):
    for file in os.listdir(path):
        if file.startswith("p"):
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
            check_json_format_flag = False
            daily_prompt = daily_routine.format(memory=person_information['memory'], current_time=todaytime)+daily_routine_prompt

            while(check_json_format_flag == False):
                daily_schedule, times = make_design(MODEL, TOKENIZER, person_information['background'], daily_prompt)
                print("行程表: {}".format(daily_schedule))
                daily_schedule, check_json_format_flag = check_json_format(daily_schedule, check_json_format_flag)

            person_information['schedule'] = daily_schedule['today_schedule']
            with open(write_file_path+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)

            print("執行時間:", times)

# 動作決定
def action_design(person_information, current_time, observe, map_info):
    check_json_format_flag = False
    action_prompt = design_action.format(memory=person_information['memory'], 
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_location=person_information["current_location"], 
                         current_time=current_time,
                         map=map_info)+design_action_prompt
    
    while(check_json_format_flag == False):
        action, times = make_design(MODEL, TOKENIZER, person_information['background'], action_prompt)
        print("動作: {}".format(action))
        action, check_json_format_flag = check_json_format(action, check_json_format_flag)

    print("執行時間:", times)
    return action["action"]

# 將動作轉換成地圖資料
def transfer_action(action, map_info, location_list):
    check_json_format_flag = False
    transfor_prompt = transfor_action.format(action_content=action, location_list=location_list, map_object=map_info)+transfor_action_prompt

    while(check_json_format_flag == False):
        transfer_action, times = transfer_model(MODEL, TOKENIZER, transfor_prompt)
        print("動作轉換: {}".format(transfer_action))
        transfer_action, check_json_format_flag = check_json_format(transfer_action, check_json_format_flag)

    print("執行時間:", times)
    return transfer_action

# 按人物順序決定動作 -> 會改成輸入個人資料決定個人動作
def person_action(path):
    for file in os.listdir(path):
        if file.startswith("p"):
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
            
            print(file)
            print(person_information['background']['name'])
            current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
            observe, map_info, location_list = get_observe(file_path, person_information)

            action = action_design(person_information, current_time, observe, map_info)
            transfered_action = transfer_action(action, map_info, location_list)

            current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
            label = "[oneself]"
            person_information['memory'] = write_memory(person_information['memory'], current_time, action, label)

            with open(write_file_path+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)
            
            write_memory_for_all_observe(write_file_path, file, person_information['current_location'], action)
            

            current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
            thought = thinking(person_information, observe, current_time)
            person_information['memory'] = write_memory(person_information['memory'], current_time, thought, "thought")

            with open(write_file_path+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)

            current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
            check_need_adjust = check_need_adjust_schedule(person_information, observe, current_time)
            if check_need_adjust:
                print("要調行程表")
                adjsuted_schedule = adjsut_schedule(person_information, observe, current_time)
            print("-"*70)

# 生成想法
def thinking(person_information, observe, current_time):
    check_json_format_flag = False
    think_prompt = create_thought.format(memory=person_information['memory'],
                         observes=observe,
                         current_location=person_information["current_location"],
                         current_time=current_time)+create_thought_prompt
    
    while(check_json_format_flag == False):
        think, times = make_design(MODEL, TOKENIZER, person_information['background'], think_prompt)
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
        check_need_adjust, times = make_design(MODEL, TOKENIZER, person_information['background'], check_need_adjust_prompt)
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
        adjsuted_schedule, times = make_design(MODEL, TOKENIZER, person_information['background'], adjsut_schedule_prompt)
        print("修改行程表: {}".format(adjsuted_schedule))
        adjsuted_schedule, check_json_format_flag = check_json_format(adjsuted_schedule, check_json_format_flag)

    print("執行時間:", times)
    return adjsuted_schedule["adjust_schedule"]


if __name__ == "__main__":
    # file_path 和 write_file_path只需要去config_new改就好
    
    # 生成行程表
    today_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A")
    daily_routine_create(file_path, today_time)

    print()
    print("="*70)
    # 決定動作並寫入記憶
    person_action(write_file_path)
    # 反應

    # 生成想法

    # 反思