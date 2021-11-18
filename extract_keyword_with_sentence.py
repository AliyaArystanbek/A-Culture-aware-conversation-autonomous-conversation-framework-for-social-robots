import urllib.request
import re
import bs4 as bs
import nltk
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords



url = "https://www.japancentre.com/it/pages/156-30-must-try-japanese-foods"
html = urllib.request.urlopen(url)
# parsing the html file
htmlParse = bs.BeautifulSoup(html, 'html.parser')


#Adding keyword into a list
keyword_file = open("keywords_japanese_food.txt", "r")
keyword_list = []
for kw in keyword_file:
  stripped_line = kw.strip()
  keyword_list.append(stripped_line)
#print(keyword_list)
# getting all the paragraphs

sentences_in_html = []
for para in htmlParse.find_all("p"):
    paragraph_text = para.get_text()
    para_sentences = paragraph_text.split(".")
    for s in para_sentences:
    	sentences_in_html.append(s.strip())
    #keywords = ['japanese']
    #keywords = open("keywords_japanese_food.txt", "r")
    #for line in keywords:
   	 #print(keywords.read().splitlines())

print(sentences_in_html)

keywords_found = []
sentences_with_keywords = []
for sent in sentences_in_html:
	tokenized_sent = [word.lower() for word in word_tokenize(sent)]
	found_keywords = []
	for keyw in keyword_list:
		if keyw in tokenized_sent:
			found_keywords.append(keyw)
	keywords_found.append(found_keywords)

print(keywords_found)
print(sentences_with_keywords)


       
