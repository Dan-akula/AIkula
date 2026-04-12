import ollama
import json

import os
from dotenv import load_dotenv
load_dotenv()
from parser import *

START_TOKEN = os.getenv("START_TOKEN")
END_TOKEN = os.getenv("END_TOKEN")
SPLIT_TOKEN = os.getenv("SPLIT_TOKEN")
SKILLS_DIR = os.getenv("SKILLS_DIR")

def generate_prompt():
    system_prompt = ('SYSTEM PROMPT\n\n'
                'Role: Ты можешь взаимодействовать с пк юзера.'
                'Пользователь имеет полные привелегия\n'
                ' Для взаимодействия с системой ты можешь использовать используя скиллы в следуюйщим формат:'
                    f'{START_TOKEN}названия скилла{SPLIT_TOKEN}команда{SPLIT_TOKEN}params в формате json{END_TOKEN}\n'
                'При возникновении ошибки сообщи пользователю честно\n'
                'Если в запросе пользователя не было запроса на использования скила, не используй.\n'
                'Если чёткой команды не было: не используй скилл и переспроси.\n'
                'Если пользователь прямо спросил/попросил: делай'
                'Если действия юзера могут угрожать системе: ОТКАЗ'
                '\n')

    skills_json = {}
    for item in os.listdir(SKILLS_DIR):
        full_path = os.path.join(SKILLS_DIR, item)
        if not os.path.isfile(full_path):
            continue  
        with open(full_path, 'r', encoding='utf-8-sig') as f:
            skills_json[item[:-5]] = json.load(f)\

    skills = "Skills:" + json.dumps(skills_json) + "\n\n"

    return system_prompt + skills 


class OllamaChat:
    def __init__(self):
        self.history = []
        self.history.append({"role": "system", "content": generate_prompt()})

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_response(self) -> str:
        response = ollama.chat(
            model="gpt-oss:120b-cloud",
            messages=self.history,
            stream=False,
            options={"temperature": 0.7, "num_predict": 512}
        )
        return response['message']['content'].strip()




def handle_prompt(chat, n=0):
    reply = chat.get_response()

    print(n, reply)


    parser = extractor(reply)

    chat.add_message("assistant", reply)

    for com in parser:

        res = executer(cmd_mapper(cmd_parser(com)))

        if not (res.stderr or res.stdout):
            continue    

        command_res = res.stderr or res.stdout

        chat.add_message("user", "stdout: " + command_res)
        
        reply = handle_prompt(chat, n+1)

    return(reply)



def main():
    chat = OllamaChat()

    while True:
        user_input = input("\nВы: ").strip()

        chat.add_message("user", user_input)
        print("Агент: ", end="", flush=True)

        print(handle_prompt(chat))


if __name__ == "__main__":
    main()