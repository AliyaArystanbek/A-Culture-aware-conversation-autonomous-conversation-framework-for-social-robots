# Imports the Google Cloud client library
#export GOOGLE_APPLICATION_CREDENTIALS="/home/aliya/Desktop/culture-aware-conversation-7ffc5840533f.json"



from google.cloud import language_v1
import argparse
import io
import json
import os

from google.cloud import language_v1
import numpy
import six
import itertools
import sys 



# Instantiates a client
client = language_v1.LanguageServiceClient()


for i in range(sys.maxsize**10):
  a = input("Human:")
#  repeat = (str(itertools.repeat(a, 20)))
  repeat1 = [(text+' ')*50 for text in a.split(' ')]
  repeat2 = ' '.join(repeat1)
  print (repeat2)
  document = language_v1.Document(
    content=repeat2, type_=language_v1.Document.Type.PLAIN_TEXT
  )
  
  #Classify the text to categories
  categories = client.classify_text(
	request={"document": document}
  ).categories
  for category in categories:
#    print(u"=" * 20)
#     print(u"{:<16}: {}".format("category", category.name))
    print(u"{}: {}".format("category", category.name))
#    print(u"{:<16}: {}".format("confidence", category.confidence))
  
# The text to analyze
#text = u"I want to eat pakora and samosa. I want to eat pakora and samosa.I want to eat pakora and samosa.I want to eat pakora and samosa."
#document = language_v1.Document(
#    content=text, type_=language_v1.Document.Type.PLAIN_TEXT
#)

# Detects the sentiment of the text
#sentiment = client.analyze_sentiment(
#    request={"document": document}
#).document_sentiment

#print("Text: {}".format(text))
#print("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))


#Classify the text to categories
#categories = client.classify_text(
#	request={"document": document}
#).categories
#for category in categories:
#	print(u"=" * 20)
#	print(u"{:<16}: {}".format("category", category.name))
#	print(u"{:<16}: {}".format("confidence", category.confidence))
