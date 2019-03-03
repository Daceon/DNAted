import sys
import requests

from flask import Flask, request, render_template
from urllib.request import urlopen
from bs4 import BeautifulSoup

### Part I: Finding gene page link from search results


# get search variable ex:Huntingtin disease
#search = input("Search: ")
#search = search.lower()

# function will take search from site
def getLocci(search):
  # seperate search string into multiple strings ex:['Huntingtin', 'disease']
  splitsearch = search.split()

  # remove string "disease" because it causes trouble
  if "disease" in splitsearch:
    splitsearch.remove("disease")

  # add + between seperate strings, replace 's by %27
  urlsearch = "+".join(splitsearch)
  urlsearch = urlsearch.replace("'", "%27")

  # specify the url ex: https://www.ncbi.nlm.nih.gov/gene/?term=homo+sapiens+Huntingtin+disease
  quote_page = "https://www.ncbi.nlm.nih.gov/gene/?term=homo+sapiens+" + urlsearch

  # scrape first link
  page = urlopen(quote_page)

  # parse the html using beautiful soup and store in variable
  soup = BeautifulSoup(page, "html.parser")

  #in case of typo or erroneous search query
  alltext = soup.get_text()
  if "The following term was not found in Gene:" in alltext:
    print("Erroneous search entry")
    return "Erroneous search entry"
    sys.exit()

  # get gene links
  linklist = []
  for link in soup.find_all("td", attrs={"class": "gene-name-id"}):
    for a in link.find_all("a", href=True):
      if "/gene/" in a.get('href'):
        linklist.append(a.get('href'))

  # in case of list that has no result
  if linklist == []:
    print("Erroneous search entry")
    return "Erroneous search entry"
    sys.exit()
        
  # get first link ex: "/gene/3064"
  firstlink = linklist[0]


  ### Part II: Scraping gene page; finding gene locci and protein name


  # create final gene page ex: "https://www.ncbi.nlm.nih.gov/gene/3064"
  quote_page = "https://www.ncbi.nlm.nih.gov" + firstlink

  # query the website and return the html to the variable ‘page’
  page = urlopen(quote_page)

  # parse the html using beautiful soup and store in variable `soup`
  soup = BeautifulSoup(page, "html.parser")

  # get gene full name
  name_box = soup.find("h1", attrs={"id": "gene-name"})
  name = name_box.text
  print (name)

  # get gene description
  dps_box = soup.find("dt", string="Summary")
  dps_box2 = dps_box.find_next_sibling()
  dps = dps_box2.text
  print (dps)

  # get gene locci
  locci_box = soup.find("dl", attrs={"class": "dl-chr-info"})
  locci = locci_box.text
  print (locci)

  #output as text
  info = name + '$' + dps + '$' + locci
  return info

app = Flask(__name__)

@app.route('/')
def my_form():
    return render_template('home.html')

""""@app.route('/', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.lower()
    print(getLoci(processed_text))
    return processed_text"""

@app.route('/',methods = ['POST', 'GET'])
def result():
    errors = []
    results = {}
    if request.method == "POST":
      try:
        searchEntry = request.form['text']
      except:
        errors.append(
          "Unable to get URL. Please make sure it's valid and try again."
        )
      query = searchEntry.lower()
    return render_template('/home.html', results = getLocci(query))

print("lol")


if __name__ == "__main__":
    app.run(debug=True)
