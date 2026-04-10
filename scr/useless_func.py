def getOllamaModels():
    models_list = []
    ollama_models = ollama.list().models
    for model in ollama_models:
        models_list.append(model.model)
    return models_list

