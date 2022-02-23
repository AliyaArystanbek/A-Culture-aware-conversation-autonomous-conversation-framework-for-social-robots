
from flask import Flask, request
from flask_restful import Api
from topics import *
from topics_utils import *
from CAIR_utils import *
from google.cloud import language_v1
from nltk.tokenize import word_tokenize 
import argparse
import io
import json
import os
import numpy
import six
import itertools
import sys 
import openai
import requests
import json
import re
import random

def get_key(val,my_dict):
    for key, value in my_dict.items():
         if val == value:
             return key
 
    return "There is no such Key"

openai.organization = "org-3afgCYP6KTHZic6sF9nBXAAt"
openai.api_key = ""


# Instantiates a client
client = language_v1.LanguageServiceClient()

for i in range(sys.maxsize**10):
    a = input("Human:")
  #  repeat = (str(itertools.repeat(a, 20)))
    repeat1 = [(text+' ')*50 for text in a.split(' ')]
    repeat2 = ' '.join(repeat1)
    print("repeat2 ",repeat2)
    document = language_v1.Document(
      content=repeat2, type_=language_v1.Document.Type.PLAIN_TEXT
    )
    print("document ",document)
    #Classify the text to categories
    categories = client.classify_text(
    request={"document": document}
    ).categories
    #print("categories ", categories)


    word_food = ["Food", "Drink", "Restaurants", "Cooking", "Recipes"]
    word_clothes = ["Clothing", "Shopping", "Fashion", "Apparel"]
    word_dance = ["Arts", "Entertainment", "Dance", "Music", "Audio"]
    word_festivals = ["Holidays", "Events", "Occasions", "Religion", "Belief", "Hobbies", "Leisure"]
    word_games = ["Sports", "Team", "Games", "Entertainment"]
    word_languages =["Language", "Foreign"]
    word_musical_instruments = ["Arts", "Entertainment", "Music", "Audio"]
    word_religion = ["Religion", "Belief"]
    word_states = ["Maps", "Government"]
    word_wedding_rituals = ["Family", "Relationships", "Marriage", "People", "Society"]
    word_list = [word_food, word_clothes, word_dance, word_festivals, word_games, word_languages, word_musical_instruments, word_religion, word_states, word_wedding_rituals]
    #word_id_list = {}
    model_id_list = ["ada:ft-personal-2022-02-14-12-57-46"," davinci:ft-personal-2022-02-16-15-16-17", "davinci:ft-personal-2022-02-17-14-54-33", "davinci:ft-personal-2022-02-17-18-27-11", 
    "davinci:ft-personal-2022-02-17-19-29-35", "davinci:ft-personal-2022-02-17-23-15-20", "ada:ft-personal-2022-02-14-12-57-77", "ada:ft-personal-2022-02-14-12-57-22", 
    "ada:ft-personal-2022-02-14-12-57-55", "ada:ft-personal-2022-02-14-12-57-88"]
    ids_list = {}
    
    for cnt, i in enumerate(model_id_list):
      #print("cnt", cnt)
      ids_list[i]=word_list[cnt]
    print("ids_list ", ids_list)
    


    #cnt=0
    #for i in word_list:
    #  for count,j in enumerate(i):
    #    word_id_list[cnt+count]=j
    #  cnt+=len(i)
    #print("word id list", word_id_list)

    

    
    if categories:
      for category in categories:
        text_category = (u"{}: {}".format("category", category.name))
        text_category_replaced = text_category.replace('/', ' ')
        print(text_category_replaced)
        text = word_tokenize(text_category_replaced)
        print("text ", text)
 #       any(x in text for x in word_list)
            
        break_out_flag = False
        for word_text in word_list:
              print("word text",word_text)
              for word in word_text:
                  print("word", word)
                  if word in text:
                    print("word in text ", word)
                    print(word)
                    model_id = get_key(word_text, ids_list)
                    print("word text", word_text)
                    print("model_id ", model_id)
                    response = openai.Completion.create(
                        model=model_id,
                        prompt=str(a) + "\nAI:",
                        temperature=0.9,
                        max_tokens=150,
                        top_p=1,
                        frequency_penalty=0.0,
                        presence_penalty=0.0,
                        stop=[".END", "}"]
                    ) 
                    print("*********&&&&&&&&&&&&&&***********", response)
                    break_out_flag = True
                    break
              if break_out_flag:
                break


              if word_list[-1] == word_text:
                if (word_text[-1] == word) and (word not in text):
                  print(word)
                  model_id = get_key(word_text, ids_list)
                  print("word text", word_text)
                  print("model_id ", model_id)
                  response = openai.Completion.create(
                      model=model_id,
                      prompt=str(a) + "\nAI:",
                      temperature=0.9,
                      max_tokens=150,
                      top_p=1,
                      frequency_penalty=0.0,
                      presence_penalty=0.0,
                      stop=[".END", "}"]
                  ) 
                  print("*********&&&&&&&&&&&&&&***********", response)
    else:
      model_id = get_key(word_text, ids_list)
      print("word text", word_text)
      print("model_id ", model_id)
      response = openai.Completion.create(
          model=model_id,
          prompt=str(a) + "\nAI:",
          temperature=0.9,
          max_tokens=150,
          top_p=1,
          frequency_penalty=0.0,
          presence_penalty=0.0,
          stop=[".END", "}"]
      ) 
      print("*********&&&&&&&&&&&&&&***********", response)


        
        #break

          
    #else:
    #    print("#############################")
    #    response = openai.Completion.create(
    #      model=random.choice(word_id_list),
    #      prompt=str(a) + "\nAI:",
    #      temperature=0.9,
    #      max_tokens=150,
    #      top_p=1,
    #      frequency_penalty=0.0,
    #      presence_penalty=0.0,
    #      stop=[".END", "}"]
    #    )
    #    print("*********&&&&&&&&&&&&&&***********", response)
    
        

