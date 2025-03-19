import requests
import json
from custom_types import Model

url = "https://openrouter.ai/api/frontend/models/find?"
headers = {"Content-Type" : "application/json; charset=utf-8"}

def main():
    response = requests.get(url)
    models_data = response.json()["data"]["models"]
    models = []

    for model_data in models_data:
        m = Model(model_data["author"],
                  model_data["short_name"],
                  model_data["slug"],
                  int(model_data["context_length"]),
                  False)
        
        if model_data["endpoint"] != None:
            m.free = (model_data["endpoint"]["variant"] == "free")
        elif "free" in model_data["slug"]:
            m.free = True;
        
        models.append(m)

    with open("models.py", "w") as f:
        f.write("from custom_types import Model\n\n")
        f.write("class Models:\n")
        
        for model in models:
            try:
                f.write("\t" + model.code_string() + "\n")
            except Exception:
                pass

if __name__ == "__main__":
    main()
