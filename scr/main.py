import ollama
import json
from parser import *


SYSTEM_PROMPT = ('Role: Ты можешь взаимодействовать с пк юзера.'
                ' Для взаимодействия с системой ты можешь использовать используя скиллы в следуюйщим формат:'
                        '<@#названия скилла|команда|params в формате json#@>\n'

            'Если в запросе пользователя не было запроса на использования скила, не используй.\n'
            'Если чёткой команды не было: не используй скилл и переспроси.\n'
            'Если пользователь прямо спросил/попросил: делай \n')
Skills_json = {
    "file":[
        {
            "create":["relative_location", "content"],
            "caption":"Все файлы будут созданы в заранее сделанной папке, являющейся относительным корнем",
            "danger_level":"save"
        }
    ]
}
SKILLS = "Skills:" + json.dumps(Skills_json) + "\n\n"

def getOllamaModels():
    models_list = []
    ollama_models = ollama.list().models
    for model in ollama_models:
        models_list.append(model.model)
    return models_list
req = 'ssss'

req = input('введите промпт\n')

models = getOllamaModels()

res = ollama.generate("gpt-oss:120b-cloud", SYSTEM_PROMPT + SKILLS + req)

print(res.response)

# Example usage when the script is executed directly
if __name__ == "__main__":
    # Extract all commands, parse each, map to executable body, and print the result
    parser = extractor(res.response)

    for com in parser:
        print(cmd_mapper(cmd_parser(com)))

        executer(cmd_mapper(cmd_parser(com)))