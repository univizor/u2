import json
import logging
import copy
import datetime
import requests
import bs4

logger = logging.getLogger('u2.agent_bio')

URL_BASE = 'http://www.doba.si/si/iskanje/results'

QUERIES = ['diplomsko', 'magistrsko']

from document.states import *
import eprints
JSON_TEMPLATE = {"school": "DOBA"}
import common


import agent_base

def stripall(s):
	s = s.replace("\t", "")
	s = s.replace("\n", "")
	s = s.replace("\r", "")
	s = s.replace(" ", "")
	return s

class Agent(agent_base.Agent):
	AGENT_NAME = "DOBA"
	AGENT_VERSION = 1

	def import_catalog(self):
		for query in QUERIES:
			logger.info('Scraping %s' % query)
			i = 1
			while True:
				url = URL_BASE + "?q=" + query + "&p=" + str(i)
				response = common.requests_get_retry(url)
				if "Ni rezultatov." in response.content:
					break
					
				soup = bs4.BeautifulSoup(response.content, "html.parser")
				for result in soup.select("h3"):
					#print result
					jdata = copy.copy(JSON_TEMPLATE)
#					print result
					agent_repository_url = result.select("a")[0].get('href')
					if not agent_repository_url.endswith("pdf"):
						continue
					doc = self.create_new_document(agent_repository_url, jdata)
				i += 1
	def import_doc(self, doc):
		(state, file) = common.download_file(doc.agent_repository_url)
		return (state, file)

agent_base.add_agent(Agent())

	