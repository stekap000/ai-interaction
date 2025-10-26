# Command line AI interaction

This is a small command line tool for interaction with AI systems (currently only LLMs).

## Dependencies

Tool relies on the OpenRouter's unified API for communication with AI models. For this reason, it needs an API key from the registered [OpenRouter](https://openrouter.ai/) account. Appart from this, you need the [Python](https://www.python.org/) interpreter and some external modules (**requests**, **json**, **os**, **datetime**). If these modules are not available on your machine, install them with [pip](https://pip.pypa.io/en/stable/installation/).

## Setup

1. Create an [OpenRouter](https://openrouter.ai/) account and generate API key.
2. Clone this repository with either of the two options:
```
git clone https://github.com/stekap000/ai-interaction
git clone git@github.com:stekap000/ai-interaction.git
```
Alternatively, you can manually download **main.py**, **custom_types.py** and **models.py** to the same folder.

3. Run the program with:
```
python main.py
```
If there is no existing configuration, you will be prompted to create the new one (**config.json**) by providing the OpenRouter API key that was previously created.

4. Setup is now done and you can use the program. If the supplied API key is valid, you can communicate with the chosen model (by default, it is set to **DeepSeek V3.1 (free)**). If the key is not valid (for any reason), you will need to supply the new one by modifying **config.json** (see below).
5. (optional) Inside the program, in order to get an up-to-date list of models, execute the **update** command (this rewrites **models.py**). After this, list free models with the **free** command (or all models with the **models** command) and pick one name from the list. Set that model as the default by using the **config.default_model** command and entering the model name when prompted (note that the **'(free)'** is also a part of the model name).
6. (optional) For more information, execute the **help** command.

## Configuration

**config.json** has the following fields:
- **api_key** - OpenRouter API key used during the communication with a chosen model.
- **timeout** - Time period, in seconds, during which the program must receive any response from the OpenRouter. If there is no response, then the communication attempt is stopped.
- **default_model** - Model that is chosen as the current model on the program startup.

There are two ways to modify the configuration:
- Manually change the fields in **config.json**. If this is done while the program is used, the changes will not be applied to the current session.
- Modification from inside the program by using the command family **config.\<attribute>**. For example, to change the API key, the command would be **config.api_key** (as if you are accesing the field of the config object). If this method is used, the changes will also apply to the current session.

## Conversations

Conversations are stored locally as JSON files in the **conversations** folder, which is automatically created on program startup if it doesn't exist. Conversation consists of the following fields:
- **name** - The full name of the conversation.
- **abbreviation** - Short reference for the conversation (used when selecting the existing conversation).
- **topic** - Topic of the conversation.
- **datetime** - Date and time of the creation of the conversation.
- **messages** - A list of messages exchanged between the user and some model.

Notice that a conversation has no information about the model that produced the responses. The reason for this is that the conversation can be a result of multiple models i.e. the user can interact with one model, switch the model during interaction, and continue interaction with another model, but the conversation stays the same. The user can also have a template conversation saved locally, and use it as a starting point for an arbitrary model.

## Usage

After running the program, you are informed about the current model that you are using and about the existing conversations. The program operates in two modes:
- **initial** - Active mode after startup, or when returning back from the conversation mode. This mode doesn't allow interactions with the model, and is used for management (for example, deletion of existing conversations).
- **conversation** - Becomes active when the user wants to start an interaction by using **new** or **old** commands (see below). The purpose of this mode is to exchange messages with the model (or models, since the model can be changed in the middle of the interaction). To return back to the **initial** mode, you can use **back** command.

Most commands can be executed in either of the two modes, but some require a specific mode. For example, the **new** command that starts the new conversation with the current model is only available in the **initial** mode. Similarly, **save** command, which saves the active conversation, is only available in the **conversation** mode.

If you need help at any point during usage, you can use the **help** command to list all available commands and their description.

## Commands

All commands, except the command family **config.\<attribute>**, have the same structure. They don't have flags and they consist of only a single word. If the command requires some input, the user will be prompted after entering the command. The command family **config.\<attribute>** is an exception since it contains more than one word, and semantically, it behaves as if you are accessing the fields of the config object.

Some commands can only be used in a specific mode (see below).

These are all available commands (output from the **help** command):
```
Commands:
        Both modes:
                clear              - Clear terminal/console.
                list               - List existing conversations.
                free               - Show free models.
                models             - Show all models.
                model              - Show the current model and allow the change of the current model.
                info               - Show the basic information for some conversation.
                exit               - Exit the program.
                update             - Grab available models.
                help               - Show this help text.
                config.<attribute> - Show the current value for the configuration attribute <attribute> and
                                     allow the change of this attribute.
        Initial mode:
                new                - Start a new conversation.
                old                - Continue old conversation.
                delete             - Delete conversation.
        Conversation mode:
                save               - Save the current conversation. If it already exists, it is updated.
                                     If it doesn't exist, then it will be created based on the prompt.
                back               - Switch from conversation to initial mode.
```

## Why?

These are all personal reasons, but here they are nonetheless:

- **Less distraction**

There are many fancier ways to interact with the models through editors, IDEs or browsers. However, I noticed that all those ways distract me during programming by shifting my focus. Since I don't use AI for code generation and restructuring (unless it is some form of throwaway or boilerplate code) I did not want to have to use the browsers or the extensions for editors/IDEs just to have a simple service of prompting a model. Rather, I decided to blend this service with the terminal that I constantly have open anyway.

- **Easy model search and switch**

While trying out various models, I noticed differences in responses where some models seem to be good for finding references, some for giving hints about random areas, some for generating good examples etc. For this reason, I wanted to have a way to easily switch models and to find new ones.

- **Free models**

For me, free models (LLMs) are more than enough. If I need a better response, I just need to better adjust my prompt, instead of using a paid version. Since I mostly use them to understand concepts (often by quickly finding proper references or getting good hints about subjects), and different models seem to be better for different areas, I wanted a way to easily access free models.

- **Conversation storing and sharing**

Whenever I wanted to carry over some conversation from one model to another, it was not seamless. An example of this is when I want to test and compare responses from multiple models to a specific sequence of messages (conversation), for the purpose of minimizing the errors/hallucinations/incorrect information that I would not notice in the response. It is also useful to have template conversations, stored locally, that I can use as injections to the model before asking it a question, thus easily altering its behaviour.

- **Arbitrary manipulation in the future**

I expect that, in time, I might have a need for an arbitrary manipulation of models and conversations. I could potentially track various data about the models, like how satisfying or correct were the answers, and then filter models based on that. I could also have a program choose a specific model automatically for me based on the conversation topic that I choose and the track record of the model for the given topic, thus minimizing the error rate. Regardless of what use case or need arises, having a decent, simple, base program, with minimal dependencies, that can easily be extended, is a plus.
