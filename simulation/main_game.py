from model import *
from prompt_new import *
from method import *
from config_new import *
from action_method import *
from character_system import *

def main():
    # 初始化地图
    with open(file_path+"map_information.json", "r", encoding="utf-8") as f:
        map_data = json.load(f)
    
    # 初始化角色系统
    for file in os.listdir(write_file_path):
        if file.startswith("p"):
            with open(write_file_path+file, "r", encoding="utf-8") as f:
                person_information = json.load(f)
                
            character_system = CharacterSystem(person_information)

    

if __name__ == "__main__":
    main()
