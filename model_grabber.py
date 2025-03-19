import requests
import json
from custom_types import Model

url = "https://openrouter.ai/api/frontend/models/find?"
headers = {"Content-Type" : "application/json; charset=utf-8"}

def main():
    response = requests.get(url)
    models_data = response.json()["data"]["models"]
    models = []

    with open("models.py", "w") as f:
        f.write("# Generated with model_grabber.py\n\n")
        f.write("from custom_types import Model\n\n")
        f.write("models = {\n")

        print(len(models_data))
        
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

            try:
                f.write("\t" + "'" + m.name + "' : " + m.code_string() + ",\n")
            except Exception as e:
                pass

        f.write("}\n")

if __name__ == "__main__":
    main()
