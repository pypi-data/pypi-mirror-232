# Utility Functions
import re, yaml
import tiktoken
from datetime import datetime

# File Name Friendly Timestamp
def get_timestamp() -> str:
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
    return timestamp

# File Name Friendly UserName
def get_safe_username(name: str) -> str:
    # Remove leading '@' and any other special characters to exclude
    return re.sub(r'[^\w\s]', '', name.lstrip('@'))

# Basic open text file function
def open_file(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as infile:
        return infile.read()

# Reads the file per line in reverse order
# Source: https://thispointer.com/python-read-a-file-in-reverse-order-line-by-line/
def read_reverse_order(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as read_obj:
        # Get all lines in a file as list to reverse order
        lines = read_obj.readlines()
        lines = [line.strip() for line in lines]
        lines = reversed(lines)
        return lines

# Read the YAML configuration file
def read_config(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    return config

# Read a plain text .prmpt file
def fetch_prompt(file_path: str):
    with open(file_path, 'r', encoding='utf-8') as prompt_file:
        prompt = prompt_file.read()
    return prompt

# Generate a Chat Session Log filename
def generate_filename(bot_name: str, user_name: str) -> str:
    timestamp = get_timestamp()
    return f'{bot_name}-{user_name}-{timestamp}.log'

# TODO: Add a function to log error messages to a file including an error type and timestamp
def log_error(error: Exception or str, error_type: str, error_filename: str):
    timestamp = get_timestamp()
    with open(error_filename, 'a') as error_file:
        error_file.write(f'{timestamp} {error_type}: {error}\n')
        # Also print the error to the console
        print(f'{timestamp} {error_type}: {error}')

# Query the maximum amount of tokens possible an OpenAI model can support
# Source: https://platform.openai.com/docs/models/overview
def max_tokens_by_model(model="gpt-3.5-turbo") -> int:
    # Update list if there are new or depreciated models
    model_tokens = {
        'gpt-4'                  : 8192,
        'gpt-4-0613'             : 8192,
        'gpt-4-32k'              : 32768,
        'gpt-4-32k-0613'         : 32768,
        'gpt-3.5-turbo'          : 4097,
        'gpt-3.5-turbo-16k'      : 16385,
        'gpt-3.5-turbo-0613'     : 4097,
        'gpt-3.5-turbo-16k-0613' : 16385,
        'babbage-002'	         : 16384,
        'davinci-002'            : 16384
    }
    if model not in model_tokens:
        raise NotImplementedError(
            f"max_tokens_by_model() is not implemented for model '{model}'.\nSee https://platform.openai.com/docs/models/overview for current list."
        )
    else:
        return model_tokens[model]

# Return the number of tokens used by a list of messages
# Source: https://github.com/openai/openai-cookbook/blob/main/examples/How_to_count_tokens_with_tiktoken.ipynb
def num_tokens_from_messages(messages: dict[str, str], model="gpt-3.5-turbo") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        print("Warning: model not found. Using cl100k_base encoding.")
        encoding = tiktoken.get_encoding("cl100k_base")
    if model in {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0613",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }:
        tokens_per_message = 3
        tokens_per_name = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4  # Every message follows <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_name = -1    # If there's a name, the role is omitted
    elif "gpt-3.5-turbo" in model:
        # Model 'gpt-3.5-turbo' may update over time -- assume latest 'gpt-3.5-turbo-0613'
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        # Model 'gpt-4' may update over time -- assume latest 'gpt-4-0613'
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(
            f"num_tokens_from_messages() is not implemented for model '{model}'.\nSee https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens."
        )
    num_tokens = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
