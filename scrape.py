#!/usr/bin/python3
import time
import logging
from urllib.request import urlopen
from bs4 import BeautifulSoup


#Logging setup
logger = logging.getLogger('spag_scraper')
logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler('spag_scraper.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)

class_prefix = "views-field views-field-field-mitglied-"
matching_dict = {
    "Name": "name",
    "Unternehmen": "unternehmen",
    "Arbeitgeber": "arbeitgeber",
    "Auftraggeber": "auftraggeber",
    "Interessenbindungen": "interessenb",
    "Unternehmen": "unternehmen",
}



class Matcher:
    def __init__(self, key, tag, class_prefix="views-field views-field-field-mitglied-", listing=False, stripping=[]):
        self.key = key
        self.tag = tag
        self.class_prefix = class_prefix
        self.listing = listing
        self.stripping = stripping

    def get_key(self):
        return self.key

    def get_tag(self):
        return self.class_prefix + self.tag
    
    def parse(self, content):
        if self.listing:
            return content.text.strip()
            print(content)
            content.find_all("li")            
            list_soup = BeautifulSoup(content, "lxml")
            list_soup.find_all("li")
        else:
            return content.text.strip()

matchers = [
    Matcher("Name", "name"),
    Matcher("Unternehmen", "unternehmen"),
    Matcher("Arbeitgeber", "arbeitgeber", listing=True),
    Matcher("Auftraggeber", "auftraggeber", listing=True),
    Matcher("Interessenbindungen", "interessenb", listing=True),
    Matcher("Unternehmen", "unternehmen", listing=True)
]

member_page_urls = []
member_names = []
for page_number in range(5):
    url = "http://www.public-affairs.ch/de/ueber-uns/mitglieder?page=%u" % page_number
    logger.debug("Scraping %s" % url)
    page = urlopen(url).read()
    soup = BeautifulSoup(page, "lxml")


    tables = soup.find_all("table", { "class" : "views-view-grid cols-4" })
    for table in tables:
        table_body = table.find('tbody')
        try:
            rows = table_body.find_all('tr')
            for tr in rows:
                cols = tr.find_all('td')
                for td in cols:
                    member_page = 'http://www.public-affairs.ch' + td.a['href'].split('?')[0]
                    member_page_urls.append(member_page)
        except:
            logger.error("no tbody")


logger.info("Members found in index: %u" % len(member_page_urls))

for member_page_url in member_page_urls:
    logger.debug("Scraping %s" % member_page_url)
    member_page = urlopen(member_page_url).read()

    member_soup = BeautifulSoup(member_page, "lxml")
    
    for matcher in matchers:
        matching_tag = matcher.get_tag()
        logger.debug(f"Matching for tag {matching_tag}")
    
        entry_content = member_soup.find_all("div", { "class" : matching_tag})
        assert(len(entry_content) < 2)
        for content in entry_content:
            content = matcher.parse(content)
            logger.info(f"{matcher.get_key()} found: {content}")
    

test_data = """    
  <div class="views-field views-field-field-mitglied-name">        <div class="field-content"><h1 id="page-title" class="page__title title"> Sacra Tomisawa-Schumacher, Vorstand</h1></div>  </div>  
  <div class="views-field views-field-views-conditional-1">        <span class="field-content">consultante</span>  </div>  
  <div class="views-field views-field-field-mitglied-unternehmen">        <div class="field-content">ellips</div>  </div>  
  <div class="views-field views-field-views-conditional-2">        <span class="field-content">Neuengasse 43</span>  </div>  
  <div class="views-field views-field-views-conditional-3">        <span class="field-content">3011 Berne</span>  </div>  
  <div class="views-field views-field-views-conditional-6">    <span class="views-label views-label-views-conditional-6">Handy: </span>    <span class="field-content">+41 79 400 11 66</span>  </div>  
  <div class="views-field views-field-views-conditional-7">        <span class="field-content"><span class="spamspan"><span class="u">info</span> [at] <span class="d">ellips.ch</span></span></span>  </div>  
  <div class="views-field views-field-views-conditional-8">        <span class="field-content"><a href="http://www.ellips.ch" target="_blank">www.ellips.ch</a></span>  </div>  
  <div class="views-field views-field-field-mitglied-curia-vista">    <span class="views-label views-label-field-mitglied-curia-vista">Curia Vista Sachgebiete: </span>    <div class="field-content">Politischer Rahmen, Parlament, Internationale Politik, Europapolitik, Soziale Fragen, Migration/Asyl, Kultur und Religion, Gesundheit, Bildung, Wissenschaft/Forschung, Umwelt, Landwirtschaft, Internationale Organisationen</div>  </div>  
  <div class="views-field views-field-field-mitglied-arbeitgeber">    <span class="views-label views-label-field-mitglied-arbeitgeber">Arbeitgeber: </span>    <div class="field-content"><div class="item-list"><ul><li class="first last">ellips</li>
</ul></div></div>  </div>  
  <div class="views-field views-field-field-mitglied-auftraggeber">    <span class="views-label views-label-field-mitglied-auftraggeber">Auftraggeber: </span>    <div class="field-content"><div class="item-list"><ul><li class="first">FER - Fédération des entreprises romandes</li>
<li>CAGE - Cercle des agriculteurs de Genève et environs</li>
<li>ASVEI - Association suisse des vignerons-encaveurs indépendants</li>
<li>Trade Club de Genève</li>
<li>imad - institution genevoise de maintien à domicile</li>
<li>Public Health Schweiz</li>
<li>Santé sexuelle suisse</li>
<li>EspeRare</li>
<li>Swisscom</li>
<li>Terre des hommes Lausanne</li>
<li>ICAN Switzerland - Campagne internationale pour l’abolition des armes nucléaires)</li>
<li>Forum Helveticum et Forum du bilinguisme</li>
<li class="last">Divers cours et formations sur le lobbying</li>
</ul></div></div>  </div>  
  <div class="views-field views-field-field-mitglied-interessenb">    <span class="views-label views-label-field-mitglied-interessenb">Weitere Interessenbindungen: </span>    <div class="field-content"><div class="item-list"><ul><li class="first">Section de Köniz du Parti socialiste suisse</li>
<li>Société des Genevois de Berne (présidente)</li>
<li class="last">Pour l&#039;ARB, déléguée Commission d’experts bilinguisme (Berne) </li>
</ul></div></div>  </div>  </div>
    </div>
"""
