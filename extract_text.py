import urllib.request
import re
from bs4 import BeautifulSoup
url = "https://www.familysearch.org/en/blog/japanese-culture" 
html = urllib.request.urlopen(url)
# parsing the html file
htmlParse = BeautifulSoup(html, 'html.parser')
  
# getting all the paragraphs
for para in htmlParse.find_all("p"):
    fileinB = para.get_text()
    print(fileinB)

