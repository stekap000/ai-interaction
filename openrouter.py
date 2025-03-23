import requests
import json
import os

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
                        return response.json()['choices'][0]['message']['content']
                except Exception:
                        return "ERROR"

class Conversation:
        def __init__(self, name = "", messages = []):
                self.name = name
                self.messages = messages

        @staticmethod
        def existing(name):
                path = "conversations/" + name + ".json"
                if os.path.isfile(path):
                        with open(path, "r") as f:
                                json_data = json.loads(f.read())
                                return Conversation(json_data["name"], json_data["messages"])
                return Conversation("", [])

        @staticmethod
        def print_all():
                print("Existing conversations:")
                for i, name in enumerate(os.listdir("conversations")):
                        print(f"\t{i + 1}. {name[:name.find('.')]}")

        def save_new(self, name):
                path = "conversations/" + name + ".json"
                with open(path, "w") as f:
                        f.write(json.dumps(self.__dict__, indent = 4))

        def save_existing(self):
                self.save(self.name)

class AIInteraction:
        def __init__(self, config_file):
                with open(config_file, "r") as f:
                        self.config = json.loads(f.read())

        def ask(self, model_name, prompt, conversation = Conversation("", []), stream = False):
                conversation.messages.append({
                        "role"    : "user",
                        "content" : prompt,
                })

                data = {
                        "model"    : models[model_name].model,
                        "messages" : conversation.messages,
                        "stream"   : stream
                }

                response = Request(self.config["api_key"]).send(api_url, data)
                if response.valid():
                        conversation.messages.append({
                                "role" : "assistant",
                                "content" : response.message,
                        })
                else:
                        return Conversation("", [])

                return conversation

        def json_stream_test(self, model_name):
                data = {
                        "model" : models[model_name].model,
                        "messages" : [{
                                "role"    : "user",
                                "content" : "What is the meaning of life?",
                                "stream"  : True
                        }]
                }
                        
                headers = {
                        "Authorization" : f"Bearer {self.config['api_key']}",
                        "Content-Type"  : "application/json"
                }

                done = False
                message_reception = False
                sse_buffer = ""
                with requests.post(api_url, headers = headers, json = data, stream = True) as response:
                        for chunk in response.iter_content(chunk_size = 128, decode_unicode = True):
                                if done:
                                        break

                                prior_length = len(sse_buffer)
                                sse_buffer += chunk
                                
                                if not message_reception:
                                        content_index = sse_buffer.find("\"content\"")
                                        if content_index != -1:
                                                temp = sse_buffer[content_index + 11:]
                                                sse_buffer = ""
                                                sse_buffer += temp
                                                print(sse_buffer)
                                                message_reception = True
                                else:
                                        refusal_index = sse_buffer.find("\"refusal\"")
                                        if refusal_index != -1:
                                                sse_buffer = sse_buffer[:(refusal_index - 2)]
                                                if refusal_index > prior_length:
                                                        print(chunk[:(refusal_index - prior_length - 2)])
                                                
                                                done = True
                                        else:
                                                print(chunk)

                print("buffer: " + sse_buffer)
                
        def stream_test(self, model_name):
                data = {
                        "model" : models[model_name].model,
                        "messages" : [{
                                "role"    : "user",
                                #"content" : "This is just an api test. Answer just with one short sentence.",
                                "content" : "What is the meaning of life?",
                                "stream"  : True
                        }]
                }
                
                headers = {
                        "Authorization" : f"Bearer {self.config['api_key']}",
                        "Content-Type"  : "application/json"
                }

                # Server is using Server Side Events
                sse_buffer = ""
                with requests.post(api_url, headers = headers, json = data, stream = True) as response:
                        for chunk in response.iter_content(chunk_size = 128, decode_unicode = True):
                                sse_buffer += chunk

                                while True:
                                        try:
                                                line_end = sse_buffer.find("\n")
                                                if line_end == -1:
                                                        break
                
                                                line = sse_buffer[:line_end].strip()
                                                sse_buffer = sse_buffer[line_end + 1:]
                                                
                                                if line.startswith("data: "):
                                                        data = line[6:]
                                                        if data == "[DONE]":
                                                                break
                                                        
                                                        try:
                                                                data_obj = json.loads(data)
                                                                content = data_obj["choices"][0]["delta"].get("content")
                                                                if content:
                                                                        print(content, end = "", flush = True)
                                                        except json.JSONDecodeError as e:
                                                                print(e)
                                                                
                                        except Exception as e:
                                                print(e)
                                                break
                                        
def main():
        # TODO(stekap): Print ai output nicely so that it always start at the same offset from the left console edge.
        
        Conversation.print_all()
        interaction = AIInteraction("config.json")

        running = True
        prompting = False
        
        while running:
                command = input("O=={=====> ").lower()
                if command == "exit":
                        running = False
                elif command == "help":
                        pass
                elif command == "new":
                        prompting = True
                        conversation = Conversation()
                        while prompting:
                                prompt = input("         > ").lower()
                                
                                if prompt == "exit":
                                        prompting = False
                                        break
                                
                                conversation = interaction.ask("DeepSeek V3 (free)", prompt, conversation, False)
                                print(f"(^_^)      {conversation.messages[-1]['content']}")
                                
                elif command.startswith("use"):
                        #conversation = Conversation.existing(conversation.name)
                        pass
                elif command.startswith("list"):
                        # list conversations
                        # list models
                        pass
        
if __name__ == "__main__":
        main()
