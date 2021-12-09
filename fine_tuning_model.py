import os
import openai
import requests
import json


openai.organization = "org-3afgCYP6KTHZic6sF9nBXAAt"
openai.api_key = "your_key"

for i in range(10):
  a = input("Human:")


  response = openai.Completion.create(
    model="FINE_TUNED_MODEL",
    prompt= str(a),
    temperature=0.0,
    max_tokens=150,
    top_p=1,
    n=1,
    best_of=3,
    frequency_penalty=0.0,
    presence_penalty=0.0,
   stop=[".END"]
  )
  print(response)
#  print ("R: "+response['choices'][0]["text"])
  print ("R: "+response['choices'][0]["text"])
  

