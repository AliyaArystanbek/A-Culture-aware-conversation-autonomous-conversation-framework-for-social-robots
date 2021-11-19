import urllib.request
import re
import bs4 as bs
import nltk
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer


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
#print(sentences_in_html)



#keyword = []
#sentences_found = []
for keyw in keyword_list:
#		found_sentences = []
#		print (keyw)
		
		#Convert list of list to list
		for word in sentences_in_html:
			  #print (word)
			  if keyw in word:
			  		tokenize_word = nltk.word_tokenize(word)
			  		#print(word)
			  		#print(tokenize_word)
			  		if len(tokenize_word) > 5:
			  				#print(tokenize_word)
			  				untokenize_word = TreebankWordDetokenizer().detokenize(tokenize_word)
			  				print(untokenize_word)

      
