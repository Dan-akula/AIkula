import json
import subprocess
import os
from dotenv import load_dotenv

load_dotenv()
# Constants defining the command encapsulation markers and split character
START_TOKEN = os.getenv("START_TOKEN")
END_TOKEN = os.getenv("END_TOKEN")
SPLIT_TOKEN = os.getenv("SPLIT_TOKEN")

# Directory where skill definition JSON files are stored
SKILLS_DIR = "./skills"


def extractor(string: str) -> list:
    """
    Extract all command strings enclosed between START_TOKEN and END_TOKEN.

    Parameters:
        string (str): The input text containing zero or more commands.

    Returns:
        list: A list of extracted command strings (without the delimiters).
    """
    result = []
    start_idx = 0
    open_len = len(START_TOKEN)
    close_len = len(END_TOKEN)

    # Keep searching for START_TOKEN until no more occurrences are found
    while string.find(START_TOKEN, start_idx) != -1:
        open_pos = string.find(START_TOKEN, start_idx)
        close_pos = string.find(END_TOKEN, open_pos + open_len)

        # Extract content between the two tokens
        content = string[open_pos + open_len:close_pos]
        result.append(content)

        # Move the search start position past the closing token
        start_idx = close_pos + close_len

    return result


def cmd_parser(cmd: str) -> dict:
    """
    Parse a raw command string into its components.

    Expected format: skill_name|cmd_name|JSON_params

    Parameters:
        cmd (str): The raw command string.

    Returns:
        dict: A dictionary with keys 'skill_name', 'cmd_name', 'params'.
    """
    spl_com = cmd.split(SPLIT_TOKEN)
    return {
        "skill_name": spl_com[0],
        "cmd_name": spl_com[1],
        "params": json.loads(spl_com[2])   # Deserialize the JSON parameters
    }


def cmd_mapper(cmd: dict) -> str:
    """
    Resolve a command dictionary into an executable body string.

    Loads the skill JSON file, retrieves the command body, and replaces
    placeholders of the form {param_name} with the actual parameter values.

    Parameters:
        cmd (dict): Command dictionary produced by cmd_parser.

    Returns:
        str: The final command body with all placeholders substituted.
    """
    # Load the skill definition file for the given skill name
    with open(f'{SKILLS_DIR}/{cmd["skill_name"]}.json', 'r') as raw_file:
        data = json.load(raw_file)

    # Obtain the body template for the specific command
    for command in data:
        if cmd["cmd_name"] == command["command"]:
            current_cmd = command
    body = current_cmd["body"]

    # Replace every occurrence of {param_name} with the corresponding value
    while body.find("}") != -1:
        open_br = body.find("{")
        close_br = body.find("}")
        param_name = body[open_br + 1:close_br]
        cmd_param = cmd["params"][param_name]

        # Perform the substitution
        body = body[:open_br] + cmd_param + body[close_br + 1:]

    return body


def executer(cmd: str):
    subprocess.run(cmd, shell=True, capture_output=True, text=True)


# Example usage when the script is executed directly
if __name__ == "__main__":
    # A test string containing a command embedded between random symbols
    test = (
        'randomsymbols\n'
        '@$<file|create|{"relative_location":"./test.txt", "content":"test"}>$@'
        'randomsymbols\nrandom'
        'Мы поняли: пользователь просит создать файл "deleteMe.txt" в корень с содержимым "test". Это явная команда, используем скилл files:create. Формируем вызов.\n'
        '<@#file|create|{"relative_location":"deleteme.txt","content":"test_file"}#@>'
    )

    # Extract all commands, parse each, map to executable body, and print the result
    parser = extractor(test)
    for com in parser:
        print(cmd_mapper(cmd_parser(com)))



    executer(cmd_mapper(cmd_parser(com)))


