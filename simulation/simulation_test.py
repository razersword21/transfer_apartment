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


# 行程表生成
def daily_routine_create(path: str, todaytime: str):
    for file in os.listdir(path):
        if file.startswith("p"):
            with open(path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)

            # 行程表生成
            daily_schedule = schedule_create(person_information, todaytime)
            person_information['schedule'] = daily_schedule['today_schedule']

            with open(write_file_path+file, "w", encoding="utf-8") as f:
                json.dump(person_information, f, ensure_ascii=False, indent=4)

# 單人動作決定鍊
def person_action(person_information, file_name, all_map_information):
    print(f"目前角色: {person_information['personality']['name']}")
    current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
    observe, map_info, location_list, all_map_information = get_observe(all_map_information, person_information)
    
    # 動作決定
    action = action_design(person_information, current_time, observe, map_info)
    # 動作轉化
    transfered_action = transfer_action(action, map_info, location_list)
    # 由轉化動作更新自己位置和使用物品
    person_information, all_map_information = get_current_location_and_used_object(person_information, transfered_action, all_map_information)
    # 寫入自己記憶
    current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
    person_information['memory'] = make_memory(person_information['memory'], None, current_time, action, "[oneself]")
    # 寫入別人記憶
    write_memory_for_all_observe(write_file_path, file_name, person_information['current_location'], action, person_information['personality']['name'])
    # 寫入地圖記憶
    all_map_information = write_map_observe(all_map_information, person_information, action)
    # 想法生成
    current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
    thought = thinking(person_information, observe, current_time)
    person_information['memory'] = make_memory(person_information['memory'], None, current_time, thought, "[thought]")
    # 動作改變
    changed_action = change_action(person_information, current_time, observe, map_info)

    return person_information, observe, all_map_information

def all_person_action(write_file_path):
    with open(file_path+"map_information.json", "r", encoding="utf-8") as f:
        all_map_information = json.load(f)
        
    for file in os.listdir(write_file_path):
        if file.startswith("p"):
            c = 5
            while(c>0):
                with open(write_file_path+file, "r", encoding="utf-8") as f:
                    person_information = json.load(f)
                
                one_person_information = copy.deepcopy(person_information)
                one_person_name = file
                print(f"第{5-c}輪")
                
                part_person_information, observe, all_map_information = person_action(one_person_information, one_person_name, all_map_information)

                with open(write_file_path+file, "w", encoding="utf-8") as f:
                    json.dump(part_person_information, f, ensure_ascii=False, indent=4)

                # 行程改變
                current_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A %H:%M")
                check_need_adjust = check_need_adjust_schedule(part_person_information, observe, current_time)
                if check_need_adjust:
                    print("需要調整行程表")
                    adjusted_schedule = adjsut_schedule(part_person_information, observe, current_time)
                    part_person_information['schedule'] = adjusted_schedule['adjust_schedule']

                    with open(write_file_path+file, "w", encoding="utf-8") as f:
                        json.dump(part_person_information, f, ensure_ascii=False, indent=4)
                
                c-=1

            # 今天結束的反思
            person_reflection_info = person_reflection(person_information)
            print("-"*70)

            with open(file_path+"map_information.json", "w", encoding="utf-8") as f:
                json.dump(all_map_information, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    # file_path 和 write_file_path只需要去config_new改就好
    
    # 生成行程表
    today_time = datetime.fromtimestamp(time.time()).strftime("%Y-%m-%d %A")
    daily_routine_create(file_path, today_time)

    print()
    print("="*70)
    print()
    # 決定動作並寫入記憶
    all_person_action(write_file_path)