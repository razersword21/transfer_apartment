from model import *
from prompt_new import *
from method import *
from config import *


from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = AutoModelForCausalLM.from_pretrained(
    model_name,
    torch_dtype="auto",
    device_map="auto"
)
TOKENIZER = AutoTokenizer.from_pretrained(model_name)


def daily_routine_create(path: str, todaytime: str):
    for file in os.listdir(path):
        if file.startswith("p"):
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
            check_json_format_flag = False
            daily_prompt = daily_routine.format(memory=person_information['memory'], current_time=todaytime)+daily_routine_prompt

            while(check_json_format_flag == False):
                daily_schedule, times = make_design(MODEL, TOKENIZER, person_information['background'], daily_prompt)
                print("生成結果: {}".format(daily_schedule))
                daily_schedule, check_json_format_flag = check_json_format(daily_schedule, check_json_format_flag)

            person_information['schedule'] = daily_schedule['today_schedule']
            with open("C:/Users/user/Desktop/setiproject/personal_information/"+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)

            print("執行時間:", times)

def action_design(person_information, current_data, observe, map_info):
    check_json_format_flag = False
    action_prompt = design_action.format(memory=person_information['memory'], 
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_location=current_data["location"], 
                         current_time=current_data["time"],
                         map=map_info)+design_action_prompt
    
    while(check_json_format_flag == False):
        action, times = make_design(MODEL, TOKENIZER, person_information['background'], action_prompt)
        print("生成結果: {}".format(action))
        action, check_json_format_flag = check_json_format(action, check_json_format_flag)

    print("執行時間:", times)
    return action["action"]

def transfer_action(action, map_info):
    check_json_format_flag = False
    transfor_prompt = transfor_action.format(action_content=action, map=map_info)+transfor_action_prompt

    while(check_json_format_flag == False):
        transfer_action, times = transfer_model(MODEL, TOKENIZER, transfor_prompt)
        print("生成結果: {}".format(transfer_action))
        transfer_action, check_json_format_flag = check_json_format(transfer_action, check_json_format_flag)

    print("執行時間:", times)
    return transfer_action

def person_action(path, current_data, observe, map_info):
    for file in os.listdir(path):
        if file.startswith("p"):
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
            
            print(file)
            print(person_information['background']['name'])

            action = action_design(person_information, current_data, observe, map_info)
            transfered_action = transfer_action(action, map_info)

            current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
            label = "[oneself]"
            person_information['memory'] = write_memory(person_information['memory'], current_time, action, label)

            with open("C:/Users/user/Desktop/setiproject/personal_information/"+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)
            
            write_memory_for_all_observe("C:/Users/user/Desktop/setiproject/personal_information/", file, current_data['location'], action)
            print("-"*70)


if __name__ == "__main__":
    file_path = "C:/Users/user/Desktop/setiproject/personal_information/origin_information/"
    today_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A")
    # daily_routine_create(file_path, today_time)

    print()
    print("="*70)
    current_data = {
        "location": "宿舍",
        "time": time.time()
    }
    with open(file_path+"map_information.json", "r", encoding="utf-8") as f:
        map_information = json.load(f)
    observe = map_information[current_data["location"]]
    map_info = remove_observe(map_information)
    person_action(file_path, current_data, observe, map_info)