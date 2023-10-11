import openai
import os

import credentials

# Have to set own API key in environment
openai.api_key = credentials.OPENAI_API_KEY

def get_alt_completion(tags, model="gpt-3.5-turbo"):
    print("tags:")
    print(tags)
    
    prompt = "Write an appropriate alternative text caption (limit to 25 words) for an image that is described using top keywords: {}".format(', '.join(tags))

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.2
    )
    
    return response.choices[0].message["content"]

def get_description_completion(tags, model="gpt-3.5-turbo"):
    print("tags:")
    print(tags)
    
    prompt = "Write an appropriate, fun instagram caption (limit to 10 words) for an image that is described using top keywords: {}".format(', '.join(tags))

    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.2
    )
    
    return response.choices[0].message["content"]
