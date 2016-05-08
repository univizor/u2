import json
import logging
import requests

import bs4
import copy
import datetime
import common
from document.states import *
logger = logging.getLogger('u2.agent_fis')



from httplib import HTTPConnection
#HTTPConnection.debuglevel = 1


import agent_base
class AgentGeneral(agent_base.Agent):
	AGENT_VERSION = 1
	def import_catalog(self):
		URLS = [
			"http://www.fis.unm.si/si/za-studente/knjiznica/e-knjiznica/diplomske-naloge-vs/",
			"http://www.fis.unm.si/si/za-studente/knjiznica/e-knjiznica/diplomske-naloge-uni/",
			"http://www.fis.unm.si/si/za-studente/knjiznica/e-knjiznica/magistrske-naloge/"
			]
		BASE_URL = "http://www.fis.unm.si"
		for url in URLS:
			r = common.requests_get_retry(url)
			soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
			formdict = {}
			for item in soup.select("article.content table tr"):
				item2 = item.find_all(text="Besedilo")
				if item2:
					agent_repository_url = item2[0].parent['href']
					if not agent_repository_url.startswith("http"):
						agent_repository_url = BASE_URL + agent_repostiory_url
					doc = self.create_new_document(agent_repository_url)


	def import_doc(self, doc):
		(download_status, file) = common.download_file(doc.agent_repository_url)
		if download_status == STATE_OK:
			return (STATE_OK, file)
		else:
			return (download_status, file)

class AgentFis(AgentGeneral):
	AGENT_NAME = "FIS"
	JSON_TEMPLATE = {"school": "Fakulteta za Informacijske Studije"}

agent_base.add_agent(AgentFis())

	