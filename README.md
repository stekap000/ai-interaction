# Command line AI interaction

This is a small command line tool for interaction with AI systems (currently only LLMs).

## Dependencies

Tool relies on the OpenRouter's unified API for communication with AI models. For this reason, it needs an API key from the registered [OpenRouter](https://openrouter.ai/) account.

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

4. Setup is now done and you can use the program. If the supplied API key is valid, you can communicate with the chosen model (by default, it is set to **DeepSeek V3.1 (free)**). If the key is not valid (for any reason), you will need to supply the new one by manually modifying **api_key** field in **config.json**, or by changing it from within the program (see below).

## Usage
