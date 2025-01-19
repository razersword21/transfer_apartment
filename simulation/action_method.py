from model import *
from prompt_new import *
from method import *
from config_new import *
import copy
from transformers import AutoModelForCausalLM, AutoTokenizer
import logging

logging.basicConfig(level=logging.INFO)

# Load and initialize the language model and tokenizer
MODEL = AutoModelForCausalLM.from_pretrained(
    model_name,  # The model name is defined in the imported configuration
    use_cache=True
).eval()

# Initialize tokenizer
TOKENIZER = AutoTokenizer.from_pretrained(model_name, use_default_system_prompt=False)

# Define a function to create a daily schedule
def schedule_create(person_information, todaytime):
    """
    Generates a daily schedule based on personality and memory.

    Args:
        person_information (dict): Contains information about the person, including memory and personality.
        todaytime (str): Current date/time.

    Returns:
        dict: A structured daily schedule.
    """
    check_json_format_flag = False
    daily_prompt = daily_routine.format(memory=person_information['memory'], current_time=todaytime) + daily_routine_prompt

    while not check_json_format_flag:
        daily_schedule, times = make_design(MODEL, TOKENIZER, person_information['personality'], daily_prompt)
        print("Schedule: {}".format(daily_schedule))
        daily_schedule, check_json_format_flag = check_json_format(daily_schedule, check_json_format_flag)

    return daily_schedule

# Alternative method to create a daily schedule
def schedule_create_method(personality, person_memory, todaytime):
    """
    Generates a daily schedule using an iterative method.

    Args:
        personality (str): Personality traits.
        person_memory (str): Memory data of the individual.
        todaytime (str): Current date/time.

    Returns:
        dict: A structured daily schedule.
    """
    check_json_format_flag = False
    daily_prompt = daily_routine.format(memory=person_memory, current_time=todaytime) + daily_routine_prompt
    required_fields = ["today_schedule"]
    
    daily_schedule = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, daily_prompt, required_fields)

    return daily_schedule

# Function to decide actions
def action_design(person_information, current_time, observe, all_location_object, location_list, nearby_characters, temp_memory):
    """
    Determines the next action based on the context.

    Args:
        person_information (dict): Person's info including schedule and memory.
        current_time (str): Current date/time.
        observe (str): Observations made by the character.
        all_location_object (list): List of all objects in the environment.
        location_list (list): List of available locations.
        nearby_characters (list): Other characters in proximity.
        temp_memory (str): Temporary memory details.

    Returns:
        str: The decided action.
    """
    check_json_format_flag = False
    action_prompt = design_action.format(memory=person_information['memory'], 
                         temp_memory=temp_memory,
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_location=person_information["current_location"], 
                         current_time=current_time,
                         location_list=location_list,
                         all_location_object=all_location_object,
                         nearby_people=nearby_characters) + design_action_prompt
    
    while not check_json_format_flag:
        action, times = make_design(MODEL, TOKENIZER, person_information['personality'], action_prompt)
        print("Action: {}".format(action))
        action, check_json_format_flag = check_json_format(action, check_json_format_flag)

    return action["action"]

# Alternative method to design action
def design_action_method(personality, memory, temp_memory, schedule, observe, current_location, current_time, location_list, all_location_object, nearby_characters):
    """
    Generates an action using an iterative approach.

    Args:
        personality (str): Personality traits.
        memory (str): Memory data of the individual.
        temp_memory (str): Temporary memory details.
        schedule (dict): The schedule of the person.
        observe (str): Observations made by the character.
        current_location (str): Current location of the person.
        current_time (str): Current date/time.
        location_list (list): List of available locations.
        all_location_object (list): List of all objects in the environment.
        nearby_characters (list): Other characters in proximity.

    Returns:
        dict: The decided action, location, and object.
    """
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
                         nearby_people=nearby_people) + design_action_prompt
    required_fields = ["action", "location", "object"]

    action = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, action_prompt, required_fields)
    return action

# Function to check additional actions
def check_additional_action_method(personality, memory, schedule, observe, current_location, current_time, nearby_characters):
    """
    Checks for additional actions the character might need to perform.

    Args:
        personality (str): Personality traits.
        memory (str): Memory data of the individual.
        schedule (dict): The schedule of the person.
        observe (str): Observations made by the character.
        current_location (str): Current location of the person.
        current_time (str): Current date/time.
        nearby_characters (list): Other characters in proximity.

    Returns:
        dict: Additional actions and related information.
    """
    check_json_format_flag = False
    nearby_people = copy.deepcopy(nearby_characters)
    nearby_people.remove(personality["name"])

    additional_action_prompt = check_addition_action.format(memory=memory, 
                         schedule=schedule, 
                         observes=observe, 
                         current_location=current_location, 
                         current_time=current_time, 
                         nearby_people=nearby_people) + check_addition_action_prompt
    required_fields = ["addtion", "person"]
    
    additional_action = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, additional_action_prompt, required_fields)
    return additional_action

# Function to determine reactions
def reaction_method(personality, memory, schedule, observe, current_location, current_time, location_list, all_location_object, nearby_characters, event_content):
    """
    Determines the character's reaction to an event.

    Args:
        personality (str): Personality traits.
        memory (str): Memory data of the individual.
        schedule (dict): The schedule of the person.
        observe (str): Observations made by the character.
        current_location (str): Current location of the person.
        current_time (str): Current date/time.
        location_list (list): List of available locations.
        all_location_object (list): List of all objects in the environment.
        nearby_characters (list): Other characters in proximity.
        event_content (str): Content of the event.

    Returns:
        dict: The character's reaction.
    """
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
                         event_content=event_content) + design_reaction_prompt
    reqired_fields = ["reaction"]
    
    reaction = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, reaction_prompt, reqired_fields)
    return reaction

# Function to generate thoughts
def thinking(person_information, observe, current_time):
    """
    Generates thoughts based on observations and memory.

    Args:
        person_information (dict): Information about the character, including memory.
        observe (str): Observations made by the character.
        current_time (str): Current date/time.

    Returns:
        str: The generated thought.
    """
    check_json_format_flag = False
    think_prompt = create_thought.format(memory=person_information['memory'],
                         observes=observe,
                         current_location=person_information["current_location"],
                         current_time=current_time) + create_thought_prompt
    
    while not check_json_format_flag:
        think, times = make_design(MODEL, TOKENIZER, person_information['personality'], think_prompt)
        print("Thought: {}".format(think))
        think, check_json_format_flag = check_json_format(think, check_json_format_flag)

    print("Execution Time:", times)
    return think["thought"]

# Function to evaluate if schedule adjustments are needed
def check_need_adjust_schedule(person_information, observe, current_time):
    """
    Determines if the character's schedule needs adjustment.

    Args:
        person_information (dict): Information about the character, including memory and schedule.
        observe (str): Observations made by the character.
        current_time (str): Current date/time.

    Returns:
        dict: Information about the need for schedule adjustments.
    """
    check_json_format_flag = False
    check_need_adjust_prompt = check_adjust.format(memory=person_information['memory'], 
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_time=current_time) + check_adjust_prompt
    
    while not check_json_format_flag:
        check_need_adjust, times = make_design(MODEL, TOKENIZER, person_information['personality'], check_need_adjust_prompt)
        print("Need Adjust Schedule: {}".format(check_need_adjust.lower()))
        check_need_adjust, check_json_format_flag = check_json_format(check_need_adjust.lower(), check_json_format_flag)

    print("Execution Time:", times)
    return check_need_adjust["need_adjust"]

# Function to adjust the schedule
def adjsut_schedule(person_information, observe, current_time):
    """
    Adjusts the character's schedule based on new observations.

    Args:
        person_information (dict): Information about the character, including memory and schedule.
        observe (str): Observations made by the character.
        current_time (str): Current date/time.

    Returns:
        dict: Adjusted schedule.
    """
    check_json_format_flag = False
    adjsut_schedule_prompt = adjust_routine.format(memory=person_information['memory'], 
                         schedule=person_information['schedule'], 
                         observes=observe, 
                         current_time=current_time) + adjust_routine_prompt
    
    while not check_json_format_flag:
        adjsuted_schedule, times = make_design(MODEL, TOKENIZER, person_information['personality'], adjsut_schedule_prompt)
        print("Adjusted Schedule: {}".format(adjsuted_schedule))
        adjsuted_schedule, check_json_format_flag = check_json_format(adjsuted_schedule, check_json_format_flag)

    print("Execution Time:", times)
    return adjsuted_schedule["adjust_schedule"]

# Function to generate dialogues
def create_dialogue_method(personality, interactive_character, memory,  observe, current_location, current_time, dialogue_history):
    """
    Creates a dialogue between the character and an interactive character.

    Args:
        personality (str): Personality traits of the character.
        interactive_character (str): The name of the interactive character.
        memory (str): Memory data of the individual.
        observe (str): Observations made by the character.
        current_location (str): Current location of the character.
        current_time (str): Current date/time.
        dialogue_history (str): Previous dialogue context.

    Returns:
        str: Generated dialogue.
    """
    check_json_format_flag = False
    dialogue_prompt = create_dialogue.format(interactive_character=interactive_character,
                         memory=memory,
                         observes=observe,
                         current_location=current_location,
                         current_time=current_time,
                         dialogue_history=dialogue_history) + create_dialogue_prompt
    required_fields = ["dialogue"]
    dialogue = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, dialogue_prompt, required_fields)
    return dialogue["dialogue"]

# Function to reflect on personality
def person_reflection(person_information):
    """
    Reflects on the character's personality traits and information.

    Args:
        person_information (dict): Contains personality traits and memory.

    Returns:
        dict: Updated personality reflection.
    """
    check_json_format_flag = False
    person_reflection_prompt = reflection.format(person_info=person_information['personality'], 
                                                 memory=person_information['memory']) + reflection_prompt
    while not check_json_format_flag:
        person_reflection_info, times = make_design(MODEL, TOKENIZER, person_information['personality'], person_reflection_prompt)
        print("Person Reflection: {}".format(person_reflection_info))
        person_reflection_info, check_json_format_flag = check_json_format(person_reflection_info, check_json_format_flag)

    print("Execution Time:", times)
    return person_reflection_info

# Function to reflect on relationships
def character_relation_thinking_method(personality, relation_person_name, origin_realationship, memory):
    """
    Reflects on relationships between the character and another person.

    Args:
        personality (str): Personality traits of the character.
        relation_person_name (str): Name of the related person.
        origin_realationship (str): Description of the original relationship.
        memory (str): Memory data of the individual.

    Returns:
        dict: Updated relationship information.
    """
    check_json_format_flag = False
    character_relation_thinking_prompt = relation_think.format(person_name=relation_person_name,
                                                                origin_relationship=origin_realationship,
                                                                memory=memory) + relation_think_prompt
    required_fields = ["relation"]
    character_relation_thinking_info = while_loop_method(check_json_format_flag, MODEL, TOKENIZER, personality, character_relation_thinking_prompt, required_fields)
    return character_relation_thinking_info['relation']

# A generalized while loop method
def while_loop_method(check_json_format_flag, model, tokenizer, personality, prompt, required_fields):
    """
    General-purpose method for executing iterative loops to ensure proper output format.

    Args:
        check_json_format_flag (bool): Indicates whether the JSON format is correct.
        model: The language model being used.
        tokenizer: The tokenizer for the model.
        personality (str): Personality traits.
        prompt (str): The generated prompt.
        required_fields (list): List of required fields in the output.

    Returns:
        dict: Validated result with the required fields.
    """
    error_count = 0
    while not check_json_format_flag:
        result, times = make_design(model, tokenizer, personality, prompt)
        result, check_json_format_flag = check_json_format(result, check_json_format_flag)
        check_json_format_flag = check_json_output(result, required_fields)

        if not check_json_format_flag:
            error_count += 1
            logging.warning("Output format error. Regenerated {} times".format(error_count))

    return result
