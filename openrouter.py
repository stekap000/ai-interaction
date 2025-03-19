import requests

import models
from custom_types import Model
from models import models

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
                return response.json()['choices'][0]['message']['content']
                

api_key = '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'
api_url = 'https://openrouter.ai/api/v1/chat/completions'

question = "This is just an api test. Answer just with one short sentence."

headers = {
	'Authorization' : f'Bearer {api_key}',
	'Content-Type'  : 'application/json'
}

data = {
        'model'    : models["DeepSeek V3 (free)"].model,
	'messages' : [{'role' : 'user', 'content' : question}]
}

def main():
        response = Request(api_key).send(api_url, data)
        if response.valid():
                print(response.message)
        
if __name__ == "__main__":
        main()
