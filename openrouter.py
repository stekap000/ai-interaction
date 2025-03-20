import requests
import json

import models
from custom_types import Model
from models import models

# TODO(stekap): Remove from global scope when structure becomes more apparent.
api_url = 'https://openrouter.ai/api/v1/chat/completions'

class ErrorCode:
        valid = 0,
        invalid = 1

class Response:
        def __init__(self, message = "", error_code = 0):
                self.message = message
                self.error_code = error_code

        def valid(self):
                return self.error_code == ErrorCode.valid

class Request:
        def __init__(self, api_key):
                self.api_key = api_key
                
                # self.messages
                # self.prompt
                # self.model
                # self.stream
                # self.transforms
                # self.models
                # self.route
                # self.provider
                
                self.temperature = 1.0 # 0.0 - 2.0
                self.top_p       = 1.0 # 0.0 - 1.0
                self.top_k       = 0.0 # > 0.0
                self.frequency_penalty = 0.0 # -2.0 - 2.0
                self.presence_penalty = 0.0 # -2.0 - 2.0
                self.repetition_penalty = 1.0 # 0.0 - 2.0
                self.min_p = 0.0 # 0.0 - 1.0
                self.top_a = 0.0 # 0.0 - 1.0
                # self.seed
                # self.max_tokens
                # self.logit_bias
                # self.logprobs
                # self.top_logprobs
                # self.response_format
                # self.structured_outputs
                # self.stop
                # self.tools
                # self.tool_choice
                # self.max_price

        def send(self, url, json):
                r = requests.post(url, json = json, headers = self.construct_headers());
                
                response = Response()
                
                if r.status_code == 200:
                        response.message = self.extract_response_message(r)
                        response.error_code = ErrorCode.valid
                else:
                        response.error_code = ErrorCode.invalid

                return response

        def construct_headers(self):
                return {
                        'Authorization' : f'Bearer {self.api_key}',
                        'Content-Type'  : 'application/json'
                }

        def extract_response_message(self, response):
                try:
                        print(response.json())
                        return response.json()['choices'][0]['message']['content']
                except Exception:
                        return "ERROR"

class AIInteraction:
        def __init__(self, config_file):
                with open(config_file, "r") as f:
                        self.config = json.loads(f.read())

        def ask(self, model_name, question, stream = True):
                data = {
                        "model" : models[model_name].model,
                        "messages" : [{
                                "role"    : "user",
                                "content" : question,
                                "stream"  : stream
                        }]
                }

                response = Request(self.config["api_key"]).send(api_url, data)
                if response.valid():
                        print(model_name + ": " + response.message)
                else:
                        print(model_name + ": ERROR::NotAvailable")

def main():
        question = "This is just an api test. Answer just with one short sentence."
        
        ai = AIInteraction("config.json")
        ai.ask("DeepSeek V3 (free)", question, False)

        #data = {
        #        'model'    : models["DeepSeek V3 (free)"].model,
	#        'messages' : [{'role' : 'user', 'content' : question}]
        #}
        #
        #for free in [value.name for key, value in models.items() if value.free]:
        #        response = Request(ai.config["api_key"]).send(api_url, data)
        #        if response.valid():
        #                try:
        #                        print(free + ": " + response.message)
        #                except Exception:
        #                        print("ERROR: " + free)
        #                        pass
        #                break
        
if __name__ == "__main__":
        main()
