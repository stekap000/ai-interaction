import requests
import json
import os
from datetime import datetime as dt

import models
from custom_types import Model
from models import models

api_url = 'https://openrouter.ai/api/v1/chat/completions'
default_config_file = "config.json"

free_models = dict([(name, model) for name, model in models.items() if model.free])

class ModelGrabber:
        @staticmethod
        def grab_models():
                url = "https://openrouter.ai/api/frontend/models/find?"
                headers = {"Content-Type" : "application/json; charset=utf-8"}

                response = requests.get(url)
                models_data = response.json()["data"]["models"]
                models = []

                with open("models.py", "w") as f:
                        f.write("# Generated with model_grabber.py\n\n")
                        f.write("from custom_types import Model\n\n")
                        f.write("models = {\n")

                        print(f"\tGrabbed {len(models_data)} models.")

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

class ErrorCode:
        valid   = 0,
        invalid = 1

class AIResponse:
        def __init__(self, message = "", error_code = 0):
                self.message = message
                self.error_code = error_code

        def valid(self):
                return self.error_code == ErrorCode.valid

class AIRequest:
        def __init__(self, interaction):
                self.interaction = interaction
                
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
                try:
                        r = requests.post(url, json = json, headers = self.construct_headers(), timeout = self.interaction.config.timeout);
                        
                        response = AIResponse()
                
                        if r.status_code == 200:
                                response.message = self.extract_response_message(r)
                                response.error_code = ErrorCode.valid
                        else:
                                print(f"Error. Reponse status code: {r.status_code}")
                                response.error_code = ErrorCode.invalid

                        return response
                except requests.exceptions.ReadTimeout:
                        return AIResponse("", ErrorCode.invalid)

        def construct_headers(self):
                return {
                        'Authorization' : f'Bearer {self.interaction.config.api_key}',
                        'Content-Type'  : 'application/json'
                }

        def extract_response_message(self, response):
                try:
                        return response.json()['choices'][0]['message']['content']
                except Exception:
                        return "ERROR"

class Conversation:
        def __init__(self, name = "", abbreviation = "", messages = [], topic = "", datetime = ""):
                self.name = name
                self.abbreviation = abbreviation
                self.messages = messages
                self.topic = topic
                self.datetime = datetime
                if self.datetime == "":
                        self.datetime = dt.today().strftime("%d.%m.%Y %H:%M")        

        @staticmethod
        def existing(abbreviation):
                path = "conversations/" + abbreviation + ".json"
                if os.path.isfile(path):
                        with open(path, "r") as f:
                                json_data = json.loads(f.read())
                                return Conversation(json_data["name"], json_data["abbreviation"], json_data["messages"], json_data["topic"], json_data["datetime"])
                return Conversation()

        @staticmethod
        def print_all():
                print("Existing conversations:")
                for i, abbreviation in enumerate(os.listdir("conversations")):
                        print(f"\t{i + 1}. {abbreviation[:abbreviation.find('.')]}")

        @staticmethod
        def info(abbreviation):
                conversation = Conversation.existing(abbreviation)

                print(f"\tName         : {conversation.name}")
                print(f"\tAbbreviation : {conversation.abbreviation}")
                print(f"\tTopic        : {conversation.topic}")
                print(f"\tDatetime     : {conversation.datetime}")
        
        def nameless(self):
                return self.name == "" and self.abbreviation == ""
                        
        def empty(self):
                return self.name == "" and self.abbreviation == "" and self.messages == []

        def save_new(self, name, abbreviation, topic):
                self.name = name
                self.abbreviation = abbreviation
                self.topic = topic
                path = "conversations/" + abbreviation + ".json"
                with open(path, "w") as f:
                        f.write(json.dumps(self.__dict__, indent = 4))

        def save_existing(self):
                self.save_new(self.name, self.abbreviation, self.topic)

        def messages_content(self):
                return [message["content"] for message in self.messages]

        def print_content(self):
                for message in self.messages:
                        if message["role"] == "user":
                                print("   ######   ")
                                print("  ##    ##  ")
                                print(" ##  ME  ## ")
                                print("  ##    ##  ")
                                print("   ######   ")
                        elif message["role"] == "assistant":
                                print("   ######   ")
                                print("  ##    ##  ")
                                print(" ##  AI  ## ")
                                print("  ##    ##  ")
                                print("   ######   ")
                        print("\n" + message["content"] + "\n")

class Config:
        def __init__(self, api_key = "", timeout = 10, default_model = "DeepSeek V3 (free)"):
                self.api_key = api_key;
                self.timeout = timeout
                self.default_model = default_model

        @staticmethod
        def load(config_file):
                try:
                        with open(config_file, "r") as f:
                                json_data = json.loads(f.read())
                                return Config(json_data["api_key"], json_data["timeout"], json_data["default_model"])
                except FileNotFoundError:
                        new_config = Config()

                        if input("Missing configuration. Create new configuration now? (y/n): ") == "y":
                                new_config.api_key = input("\tAPI key: ")
                                # Set default timeout and model without asking.
                                new_config.timeout = 10
                                new_config.default_model = "DeepSeek V3 (free)"
                                print("\tDefault model set to \"DeepSeek V3 (free)\". You can change it after.")

                                new_config.save(config_file)
                                print(f"\tConfiguration created. File name: {config_file}\n")

                                return new_config
                        else:
                                exit()
                except:
                        pass

        def save(self, config_file):
                with open(config_file, "w") as f:
                        f.write(json.dumps(self.__dict__, indent = 4))

class AIInteraction:
        def __init__(self, config):
                self.config = config
                self.ai_request = AIRequest(self)

        def ask(self, model_name, prompt, conversation = Conversation(), stream = False):
                conversation.messages.append({
                        "role"    : "user",
                        "content" : prompt,
                })

                # Since we take model parameter from 'slug' when using model grabber, we make sure that the ":free"
                # is at the end if the model is free, since the api requires this.
                model_attrib = models[model_name].model
                if models[model_name].free and ":free" not in model_attrib:
                        model_attrib += ":free"

                data = {
                        "model"    : model_attrib,
                        "messages" : conversation.messages,
                        "stream"   : stream
                }

                ai_response = self.ai_request.send(api_url, data)
                
                if ai_response.valid():
                        conversation.messages.append({
                                "role" : "assistant",
                                "content" : ai_response.message,
                        })
                else:
                        print(f"Model [{model_name}] did not respond.")
                        return Conversation()

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
                        "Authorization" : f"Bearer {self.config.api_key}",
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
                        "Authorization" : f"Bearer {self.config.api_key}",
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

class CommandHandler:
        def __init__(self, cli):
                self.cli = cli
        


        def new(self):
                if self.cli.state == CLIState.initial:
                        self.cli.state = CLIState.conversation
                        self.cli.conversation = Conversation()

        def old(self):
                if self.cli.state == CLIState.initial:
                        abbreviation = input("\tAbbreviation : ")
                        self.cli.conversation = Conversation.existing(abbreviation)
                        if self.cli.conversation.empty():
                                print("\tConversation does not exist.")
                        else:
                                self.cli.state = CLIState.conversation
                                print("")
                                self.cli.conversation.print_content()

        def save(self):
                if self.cli.state == CLIState.conversation:
                        if self.cli.conversation.nameless():
                                name         = input("\tName         : ")
                                abbreviation = input("\tAbbreviation : ")
                                topic        = input("\tTopic        : ")
                                self.cli.conversation.save_new(name, abbreviation, topic)
                        else:
                                self.cli.conversation.save_existing()

                        print("\tSaved.")

        def delete(self):
                if self.cli.state == CLIState.initial:
                        abbreviation = input("\tAbbreviation: ")
                        if input(f"\tConversation [{abbreviation}] will be deleted. Confirm (y/n) : ") == "y":
                                try:
                                        os.remove("conversations/" + abbreviation + ".json")
                                        print("\tConversation deleted.")
                                except Exception:
                                        print("\tConversation does not exist.")
                        else:
                                print("\tDeletion canceled.")

        def clear(self):
                os.system("cls" if os.name == "nt" else "clear")

        def list(self):
                Conversation.print_all()

        def free(self):
                print(f"Free models (Total Count: {len(free_models)}):")
                for model in free_models.values():
                        print(f"\t{model.name}")

        def models(self):
                print(f"Available models (Total Count: {len(models)}):")
                for model in models.values():
                        print(f"\t{model.name}")

        def model(self):
                print(f"Current model: {self.cli.current_model}")
                new_model = input("\tNew model: ")
                if new_model in models:
                        self.cli.current_model = new_model
                else:
                        print("\tGiven model doesn't exist.")

        def info(self):
                Conversation.info(input("\tAbbreviation : "))

        def back(self):
                if self.cli.state == CLIState.conversation:
                        self.cli.state = CLIState.initial
                        self.cli.conversation = Conversation()

        def exit(self):
                self.cli.running = False

        def update(self):
                if self.cli.state == CLIState.initial:
                        ModelGrabber.grab_models()
                        exit()

        def help(self):
                print("Commands:")
                print("\tnew                - Start a new conversation.")
                print("\told                - Continue old conversation.")
                print("\tsave               - Save the current conversation. If it already exists, it is updated.")
                print("\t                     If it doesn't exist, then it will be created based on the prompt.")
                print("\tdelete             - Delete conversation.")
                print("\tclear              - Clear terminal/console.")
                print("\tlist               - List existing conversations.")
                print("\tfree               - Show free models.")
                print("\tmodels             - Show all models.")
                print("\tmodel              - Show the current model and allow the change of the current model.")
                print("\tinfo               - Show the basic information for some conversation.")
                print("\tback               - Switch from conversation to initial mode.")
                print("\texit               - Exit the program.")
                print("\thelp               - Show this help text.")
                print("\tconfig.<attribute> - Show the current value for the configuration attribute <attribute> and")
                print("\t                     allow the change of this attribute.")

        def execute(self, command):
                try:
                        if command == "":
                                return True

                        CommandHandler.__dict__[command](self)
                        return True
                except Exception:
                        return False

# TODO(stekap): Maybe add support to go back through multiple states. Currently it is not needed.
class CLIState:
        initial      = 0
        conversation = 1

class CLI:
        def __init__(self, config):
                self.config = config
                self.interaction = AIInteraction(config)
                self.state = CLIState.initial
                self.current_model = self.config.default_model
                self.conversation = Conversation()
                self.command_handler = CommandHandler(self)
                self.running = False

        def start(self):
                print("Enter 'help' for short help manual.\n")
                print(f"Current model: {self.current_model}\n")
                self.command_handler.list()
                print("")

                self.running = True
                prompting = False

                while self.running:
                        command = input(f"({'conversation' if self.state == CLIState.conversation else 'initial'}) > ")

                        if self.command_handler.execute(command.lower()):
                                continue

                        if command.lower().startswith("config."):
                                config_attribute = command.split(".")[1]
                                attribute_value = getattr(self.config, config_attribute, None)
                                if attribute_value != None:
                                        print(f"\tOld value: {attribute_value}")
                                        new_attribute_value = input(f"\tNew value: ")
                                        if new_attribute_value != "":
                                                if type(attribute_value) == type(0):
                                                        try:
                                                                new_attribute_value = int(new_attribute_value)
                                                        except:
                                                                print("\tInvalid input. Value must be of integer type for this attribute.")
                                                                continue

                                                setattr(self.config, config_attribute, new_attribute_value)
                                                self.config.save(default_config_file)
                                                print("\tConfiguration updated.")
                                continue

                        if self.state == CLIState.conversation:
                                print("")
                                self.conversation = self.interaction.ask(self.current_model, command, self.conversation, False)
                                
                                if self.conversation.empty():
                                        print("AI not available. Returning to initial state.\n")
                                        self.state = CLIState.initial
                                else:
                                        response = self.conversation.messages[-1]["content"]
                                        print(response)
                                        print("")
                        elif self.state == CLIState.initial:
                                pass

# TODO(stekap): Handle kill signal (ctrl c).
#
# TODO(stekap): Add conversation compression that is also done by AI, so that we send only the main points and thus
#               increase the speed of conversation transmission. Also, we keep less information locally.
# TODO(stekap): Add UI that can be started with a command, which will display the chat more nicely and correctly display
#               things like latex.

def main():
        CLI(Config.load(default_config_file)).start()

if __name__ == "__main__":
        main()
