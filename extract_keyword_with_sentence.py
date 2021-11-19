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

# getting all the paragraphs
fileinF = []
for para in htmlParse.find_all("p"):

    fileinE = para.get_text()
    #print(fileinE)
    li = list(fileinE.split("."))
    keywords = ['japanese']
    #print(li)
    keywordfile = open('/home/aliya/Desktop/keywords_japanese_food.txt')



    for sent in li:
        tokenized_sent = [word.lower() for word in word_tokenize(sent)]

        if any(keyw in tokenized_sent for keyw in keywords):
            fileinF.append(sent)
            
list_with_keyword = fileinF
print(list_with_keyword)
#text_with_keyword = '. '.join([str(elem) for elem in list_with_keyword])
#print(text_with_keyword)


       
