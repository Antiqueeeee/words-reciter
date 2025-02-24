import os, sys
current_path = os.path.abspath(os.path.join(__file__, os.pardir))
project_path = os.path.abspath(os.path.join(current_path, os.pardir))
sys.path.append(project_path)


from fastapi import responses
from openai import OpenAI
import json

from config import *
class GPTEngine:
    def __init__(self, model = DEFAULT_GPT_MODEL):
        self.model_name = model
        self.base_url = GPT_MODELS[model]["base_url"]
        self.api_key = GPT_MODELS[model]["api_key"]
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, prompt = None, message = list(), left_tag = None, right_tag = None):
        if prompt is None and len(message) == 0:
            raise ValueError("Either prompt or message must be provided")

        message.append({"role" : "user", "content" : prompt})
        for m in message:
            print(m)
        params = {
            "messages" : message,
            "model" : self.model_name
        }
        response = self.client.chat.completions.create(**params).choices[0].message.content
        print(response)
        print()
        if left_tag is not None and right_tag is not None:
            response = self.load_json_from_response(response, left_tag, right_tag)
        
        return response

    def load_json_from_response(self, response, left_tag, right_tag):
        try:
            left_index = response.find(left_tag)
        except :
            left_index = -1
        
        try:
            right_index = response.rfind(right_tag) + 1
        except :
            right_index = -1
        
        if left_index != -1 and right_index != -1:
            content = json.loads(response[left_index : right_index])
            return content
        else:
            raise ValueError("Left or right tag not found in response:\n" + response)

if __name__ == "__main__":
    gpt = GPTEngine(model = "deepseek-chat")
    prompt = WORD_COMPLETION_TEMPLATE.format(word="project")
    response = gpt.chat(prompt = prompt,left_tag="{", right_tag="}")
    print(response)
