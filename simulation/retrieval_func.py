from model import *  # Importing necessary modules and functions from the model file
from config_new import *  # Importing configuration settings
from transformers import AutoModelForCausalLM, AutoTokenizer  # Importing Hugging Face's Transformer model utilities

# Unified processing function
def process_and_score_memories(memory_string, current_situation, model, tokenizer, top_k=100):
    # Split the input memory string into individual memory entries based on newlines
    memories = memory_string.strip().split("\n")
    memory_dict = {}  # Dictionary to store processed memory data

    for idx, memory in enumerate(memories, start=1):
        # Extract the timestamp and content from each memory
        time_end_idx = memory.find("[")  # Find the end of the timestamp
        content_start_idx = memory.find("[")  # Find the start of the content tag

        if time_end_idx != -1 and content_start_idx != -1:
            # Extract timestamp and content
            time = memory[:time_end_idx].strip()  # Extract the timestamp part
            content = memory[content_start_idx:]  # Extract the memory content

            # Prepare prompt for the model to evaluate importance and relevance
            prompt = (f"Given the current situation: '{current_situation}', "
                      f"estimate the importance and relevance (1-10 scale) for this memory: '{content}'. "
                      "Respond with two integers in the format: importance,relevance.")

            # Get response from the model (assuming transfer_model is a function defined in the model module)
            response, _ = transfer_model(model, tokenizer, prompt)

            # Parse the model's response to extract importance and relevance
            try:
                importance, relevance = map(int, response.split(","))  # Split the response into two integers
                importance_normalized = importance / 10.0  # Normalize importance to [0, 1]
                relevance_normalized = relevance / 10.0  # Normalize relevance to [0, 1]
                recently = 0.0  # Placeholder for recency score
                last_retrieved = None  # Placeholder for the last retrieval timestamp

                # Add processed memory to the dictionary
                memory_dict[idx] = {
                    "time": time,  # Memory timestamp
                    "content": content,  # Memory content
                    "recency": recently,  # Recency score (default 0.0)
                    "importance": importance_normalized,  # Normalized importance score
                    "relevance": relevance_normalized,  # Normalized relevance score
                    "score_sum": recently + importance_normalized + relevance_normalized,  # Total score
                    "last_retrieved": last_retrieved  # Last retrieval timestamp
                }
            except ValueError:
                # Handle cases where the model's response is not in the expected format
                print(f"Error: Retrieval function did not return correct format for memory {idx}. Response: '{response}'")
                memory_dict[idx] = {
                    "time": time,  # Memory timestamp
                    "content": content,  # Memory content
                    "recency": 0.0,  # Default recency score
                    "importance": 0.0,  # Default importance score
                    "relevance": 0.0,  # Default relevance score
                    "score_sum": 0.0,  # Default total score
                    "last_retrieved": last_retrieved  # Default last retrieval timestamp
                }

    # If top_k is greater than the total number of memories, return the entire dictionary
    if top_k >= len(memory_dict):
        return memory_dict

    # Sort memories by their score_sum in descending order and select the top_k entries
    sorted_memories = sorted(memory_dict.items(), key=lambda x: x[1]["score_sum"], reverse=True)
    top_k_memories = {k: v for k, v in sorted_memories[:top_k]}

    return top_k_memories  # Return the top-k most relevant memories

# Example usage
def retirval_func(memory_string, query) -> dict:
    # Load the pre-trained model and tokenizer
    MODEL = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype="auto",  # Automatically selects the appropriate data type for the model
        device_map="auto"  # Automatically assigns devices (e.g., CPU/GPU) for the model
    )
    TOKENIZER = AutoTokenizer.from_pretrained(model_name)  # Load the tokenizer

    # Process and rank the memories
    result_dict = process_and_score_memories(memory_string, query, MODEL, TOKENIZER)
    print(result_dict)  # Print the results for debugging or analysis
    return result_dict  # Return the ranked memories
"""
    Function Introduction:
    -----------------------
    Author: Xian-Hong, Wang

    The `retrival_func` serves as a wrapper to load the pre-trained Transformer model and tokenizer,
    and to process a memory string and a given current situation. It leverages the 
    `process_and_score_memories` function to evaluate and score memories based on their relevance 
    and importance to the current situation.

    Inputs:
    - `memory_string`: A string containing memories formatted as 'timestamp [category]content'.
    - `current_situation`: A string describing the user's current context.

    Outputs:
    - Returns a dictionary containing memories ranked by their relevance and importance scores.
      The dictionary keys are memory indices, and the values are metadata including:
        - time: Memory timestamp
        - content:  Memory content
        - recency: normalize score
        - importance: normalized score
        - relevance: normalized score
        - score_sum: sum of importance, relevance, and recency
        - last_retrieved: time of last retrieved.

    Usage:
    - This function is used to filter and prioritize memories based on contextual information,
      making it ideal for applications like memory-augmented AI systems or personal assistants.
    """

if __name__ == "__main__":
    # Sample input: A string containing memories with timestamps and content
    sample_memory_string = "2025-01-05 Sunday 21:15 [others]陳宇翔stay\n2025-01-05 Sunday 21:18 [others]陳宇翔stay\n2025-01-05 Sunday 21:18 [others]陳宇翔stay\n2025-01-05 Sunday 21:22 [others]陳宇翔開始進行第一次的冥想練習\n2025-01-05 Sunday 21:24 [others]陳宇翔開始進行第一次的冥想練習\n2025-01-05 Sunday 21:32 [others]陳宇翔繼續進行第一次的冥想練習\n2025-01-05 Sunday 21:35 [others]陳宇翔開始進行第一次的冥想練習\n2025-01-05 Sunday 21:36 [others]陳宇翔開始今天的冥想練習\n2025-01-05 Sunday 21:36 [others]陳宇翔開始今天的冥想練習\n2025-01-05 Sunday 21:37 [others]陳宇翔進行今天的冥想練習\n2025-01-05 Sunday 21:37 [others]陳宇翔繼續今天的冥想練習\n2025-01-05 Sunday 21:38 [others]李子建進入健身房進行健身運動\n2025-01-05 Sunday 22:10 [others]陳宇翔stay\n2025-01-05 Sunday 22:10 [others]陳宇翔stay\n"
    # Sample input: A description of the current situation
    sample_current_situation = "Starting university life and adjusting to a new environment."

    # Run the retrieval function with sample inputs
    retirval_func(sample_memory_string, sample_current_situation)