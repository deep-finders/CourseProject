from goose import Goose
import urllib2
#from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.chrome.service import Service
#from webdriver_manager.chrome import ChromeDriverManager
#from selenium.webdriver.common.by import By

#url = "https://newjersey.craigslist.org/cps/d/closter-websites-for-business/7401625647.html"
#url = "https://en.wikipedia.org/wiki/Climate_change"
url = "https://amazon.com/Samsung-Electronics-Galaxy-Watch-Active2/dp/B086RQHS3T?ref_=Oct_DLandingS_D_08df7a57_61&smid=ATVPDKIKX0DER"

#Initialize driver
#s=Service(ChromeDriverManager().install())
#driver = webdriver.Chrome(service=s)
#driver.maximize_window()

#Simulating input that comes from POST request
#driver.get(url)
#documentHtml = driver.page_source
#print(documentHtml)


g = Goose()
#article = g.extract(raw_html=documentHtml)
article = g.extract(url=url)
print(article.title)
print(article.cleaned_text)