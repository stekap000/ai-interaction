import requests

api_key = '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'
api_url = 'https://openrouter.ai/api/v1/chat/completions'

headers = {
	'Authorization' : f'Bearer {api_key}',
	'Content-Type'  : 'application/json'
}

data = {
	'model'    : 'deepseek/deepseek-chat:free',
	'messages' : [{'role' : 'user', 'content' : 'What is the purpose of Lebesgue integral?'}]
}

response = requests.post(api_url, json=data, headers=headers)

if response.status_code == 200:
	print('Response: ', response.json()['choices'][0]['message']['content'])
else:
	print('Failed. Status code: ', response.status_code)
