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
                ' Для взаимодействия с системой ты можешь использовать используя скиллы в следуюйщим формат:'
                    f'{START_TOKEN}названия скилла{SPLIT_TOKEN}команда{SPLIT_TOKEN}params в формате json{END_TOKEN}\n'

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





#!/usr/bin/env python3
"""
Простой консольный чат-агент с использованием библиотеки ollama.
Не использует прямые HTTP-запросы к API, только высокоуровневые вызовы.
"""

import ollama  # pip install ollama

DEFAULT_MODEL = "llama3.2"
SYSTEM_PROMPT = "Ты полезный и дружелюбный ассистент."

class OllamaChat:
    def __init__(self, model: str = DEFAULT_MODEL, system_prompt: str = SYSTEM_PROMPT):
        self.model = model
        self.history = []
        if system_prompt:
            self.history.append({"role": "system", "content": system_prompt})

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_response(self) -> str:
        response = ollama.chat(
            model=self.model,
            messages=self.history,
            stream=False,
            options={"temperature": 0.7, "num_predict": 512}
        )
        return response['message']['content'].strip()


def main():
    chat = OllamaChat(model="gpt-oss:120b-cloud")
    chat.add_message("assistant", generate_prompt())

    while True:
        user_input = input("\nВы: ").strip()

        chat.add_message("user", user_input)
        print("Агент: ", end="", flush=True)

        reply = chat.get_response()

        parser = extractor(reply)
        for com in parser:
            print(cmd_mapper(cmd_parser(com)))
            executer(cmd_mapper(cmd_parser(com)))

        print(reply)
        chat.add_message("assistant", reply)

if __name__ == "__main__":
    main()
