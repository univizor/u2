import logging
import bs4
import copy
import datetime
import common
from document.states import *
logger = logging.getLogger('u2.agent_up')

YEARS = range(1997, datetime.date.today().year)

#from document.states import *
import eprints
JSON_TEMPLATE = {"school": "Univerza na Primorskem"}

SEARCH_URL = "http://repozitorij.upr.si/Brskanje2.php?kat1=letoIzida&kat2="

import agent_base
class Agent(agent_base.Agent):
	AGENT_NAME = "UP"
	AGENT_VERSION = 1

	def import_catalog(self):
		for year in YEARS:
			logger.info("Scrapping year " + str(year))
			for page in xrange (1, 1000):
				url = SEARCH_URL + str(year) + "&page=" + str(page)

				r = common.requests_get_retry(url)
				soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
				total = soup.select(".Stat")[0]
				s = total.text.split(" ")
				if s[2] == s[4]:
					break
				for item in soup.select(".Besedilo"):
					agent_repository_url = "http://repozitorij.upr.si/" + item.select("a")[0]['href']
					doc = self.create_new_document(agent_repository_url)
#					print agent_repository_url
	def import_doc(self, doc):
		# example url: http://repozitorij.upr.si/IzpisGradiva.php?id=976&lang=slv
		# three steps are needed:
		# 1) extract pdf url
		# 2) follow it to get to cookied yes-page
		# 3) download the final pdf
		jdata = copy.copy(JSON_TEMPLATE)
		r = common.requests_get_retry(doc.agent_repository_url)
		soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
		datoteke = soup.find_all(text="Datoteke:")
		urlname = datoteke[0].parent.next_sibling.select("a")[0].text.strip(" ")
		print urlname
		if not urlname.endswith(".pdf"):
			# here there are a lot of pointers to third parties, but we only support direct links to pdfs
			return (STATE_PERM_FAIL, None)
		url = datoteke[0].parent.next_sibling.select("a")[0]["href"]
		print url
		raise Excetion("x")
#		return (status, file)

agent_base.add_agent(Agent())

	