import logging
import requests

import bs4
import copy
import datetime
import common
from document.states import *
logger = logging.getLogger('u2.agent_up')



from httplib import HTTPConnection
#HTTPConnection.debuglevel = 1


YEARS = range(1997, datetime.date.today().year)

#from document.states import *
import eprints

import agent_base
class AgentGeneral(agent_base.Agent):
	AGENT_VERSION = 1
	def import_catalog(self):
		for year in YEARS:
			logger.info("Scrapping year " + str(year))
			for page in xrange (1, 1000):
				url = self.BASE_URL + "Brskanje2.php?kat1=letoIzida&kat2=" + str(year) + "&page=" + str(page)

				r = common.requests_get_retry(url)
				soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
				total = soup.select(".Stat")[0]
				s = total.text.split(" ")
				if s[2] == s[4]:
					break
				for item in soup.select(".Besedilo"):
					agent_repository_url = self.BASE_URL + item.select("a")[0]['href']
					logger.debug("URL:" + agent_repository_url)
					doc = self.create_new_document(agent_repository_url)
	def import_doc(self, doc):
		# example url: http://repozitorij.upr.si/IzpisGradiva.php?id=976&lang=slv
		# three steps are needed:
		# 1) extract pdf url
		# 2) follow it to get to cookied yes-page
		# 3) download the final pdf
		jdata = copy.copy(self.JSON_TEMPLATE)
		print doc.agent_repository_url
		r = common.requests_get_retry(doc.agent_repository_url)
		soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")


		vrsta = ""
		vrstatag = soup.find_all(text="Tipologija:")
		if vrstatag:
			vrsta += vrstatag[0].parent.next_sibling.text.lower()
		vrstatag = soup.find_all(text="Vrsta gradiva:")
		if vrstatag:
			vrsta += vrstatag[0].parent.next_sibling.text.lower()
		if "magistr" not in vrsta and "diplom" not in vrsta and "doktor" not in vrsta:
			# we could also expand to download other types of works
			logger.info("Not sought after work type: %s" % vrsta)
			return (STATE_PERM_FAIL, None)

		datoteke = soup.find_all(text="Datoteke:")
		urlname = datoteke[0].parent.next_sibling.select("a")[0].text.strip(" ")
		print urlname
		if not urlname.lower().endswith(".pdf"):
			# here there are a lot of pointers to third parties, but we only support direct links to pdfs
			return (STATE_PERM_FAIL, None)
		url = datoteke[0].parent.next_sibling.select("a")[0]["href"]
		if not url.startswith("http"):
			url = self.BASE_URL + url
		'''
		# I couldn't make this work
		with requests.Session() as s:
		    r = s.get(url)
		    soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
		    tags = soup.select("form input")
		    key = tags[0]['value']
		    print key
		    r = s.post(url, data="key=" + key, allow_redirects=True)
		    print r.status_code
		    print r.url
#		    print r.content
#		    r = s.post(URL2, data="username and password data payload")

		'''
		# let's cheat and assume that for the works we're interested in, urlname is the real name
		(download_status, file) = common.download_file(urlname)
		if download_status == STATE_OK:
			return (STATE_OK, file)
		else:
			return (download_status, file)

#		return (status, file)

class AgentUP(AgentGeneral):
	AGENT_NAME = "UP"
	BASE_URL = "http://repozitorij.upr.si/"
	JSON_TEMPLATE = {"school": "Univerza na Primorskem"}

class AgentUNG(AgentGeneral):
	AGENT_NAME = "UNG"
	BASE_URL = "http://repozitorij.ung.si/"
	JSON_TEMPLATE = {"school": "Univerza v Novi Gorici"}

class AgentUMB(AgentGeneral):
	AGENT_NAME = "UMB"
	BASE_URL = "http://dk.um.si/"
	JSON_TEMPLATE = {"school": "Univerza v Mariboru"}


agent_base.add_agent(AgentUP())
agent_base.add_agent(AgentUNG())
agent_base.add_agent(AgentUMB())

	