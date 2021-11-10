#Libraries needed
#html5lib, pip install html5lib -- html5lib used by sentence parser
#htmlst, pip install htmlst -- sentence parser <- not used, in the end, had to create a local copy to modify the library given parsing issues found with newer tags
#selenium, pip install selenium -- used for testing, to simulate info that comes from Chrome extension POST
#webdriver_manager, pipi install webdriver_manager -- to install chrome driver for selenium

from HTMLSentenceTokenizer import HTMLSentenceTokenizer
import nltk #needed for sentence tokenization

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from lxml.html.clean import Cleaner
from pathlib import Path

#Initialize driver
s=Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s)
driver.maximize_window()


#Simulating input that comes from POST request
path = Path(__file__).parent / "../parser/Sample%20websites/climate_change.html"
path = "file://" + str(path)
driver.get(path)
#driver.get("file:///Users/main/Documents/Text%20Information%20Systems/CourseProject/parser/Sample%20websites/climate_change.html")
documentHtml = driver.page_source
documentHtml = documentHtml.encode("utf8")
#print(documentHtml)
#cleaner = Cleaner(style=True)
#documentHtml = cleaner.clean_html(documentHtml)

#print(documentHtml)

#Sentence parser
nltk.download('punkt')
parsed_sentences = HTMLSentenceTokenizer().feed(documentHtml)
print(parsed_sentences)