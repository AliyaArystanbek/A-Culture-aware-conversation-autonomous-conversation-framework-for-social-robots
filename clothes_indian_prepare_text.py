import urllib.request
import re
import bs4 as bs
import nltk
import json
from nltk import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.tokenize.treebank import TreebankWordDetokenizer
from urllib.request import Request, urlopen


req = Request('https://en.wikipedia.org/wiki/Clothing_in_India', headers={'User-Agent': 'Mozilla/5.0'})
html = urlopen(req).read()
html = urllib.request.urlopen(req)
# parsing the html file
htmlParse = bs.BeautifulSoup(html, 'html.parser')


#Adding keyword into a list
keyword_file = open("clothes_indian_kw.txt", "r")
keyword_list = []
for kw in keyword_file:
  stripped_line = kw.strip()
  keyword_list.append(stripped_line.lower())
#print(keyword_list)

# getting all the paragraphs

sentences_in_html = []
for para in htmlParse.find_all("p"):
#    print(para)
    paragraph_text = para.get_text()
    para_sentences = paragraph_text.split(".")
    for s in para_sentences:
    	sentences_in_html.append(s.strip().lower())
#    	print(sentences_in_html)



#keyword = []
#sentences_found = []
untokenize_word_list = []
for keyw in keyword_list:
#		found_sentences = []
#		print (keyw)
		
		#Convert list of list to list
		for word in sentences_in_html:
#			  print (word)
			  if keyw in word:
			  		tokenize_word = nltk.word_tokenize(word)
			  		#print(word)
			  		#print(tokenize_word)
			  		if len(tokenize_word) > 5:
			  				#print(tokenize_word)
			  				untokenize_word = TreebankWordDetokenizer().detokenize(tokenize_word)
			  				untokenize_word_list.append(untokenize_word)
#			  				print(untokenize_word_list)


def main():
		f= open("clothes_indian_text.txt","w+")
		
#		for keyw in range(len(keyword_list)):
		for keyw in keyword_list:
				for sent in untokenize_word_list:
						if keyw in sent:
							 sent_capitalized = sent.capitalize()
							 #print(keyw)
							 f.write("{" + "\"" +"prompt" + "\"" + ":" + " " + "\"" + keyw + "\"" + "," + " " + "\"" + "completion" + "\"" + ":" + " " + "\"" + sent_capitalized + "."  + "END" + "\"" + "}" + "\r\n")

		f.close()
		
if __name__=="__main__":
		main()



