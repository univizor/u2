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


import agent_base
class AgentGeneral(agent_base.Agent):
	AGENT_VERSION = 1
	def import_catalog(self):
		TOP_URLS = [
			"http://www.doba.si/si/iskanje/results?q=diplomska",
			"http://www.doba.si/si/iskanje/results?q=diplomsko",
			"http://www.doba.si/si/iskanje/results?q=magistrska",
			"http://www.doba.si/si/iskanje/results?q=magistrsko",
			]
		for topurl in TOP_URLS:
			for page in xrange (1, 10000):
				url = topurl + "&p=" + str(page)

				r = common.requests_get_retry(url)
				soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
				items = soup.select("li p a")
				if not items:
					break
				for item in items:
					agent_repository_url = item['href']
					if not agent_repository_url.lower().endswith(".pdf"):
						continue
					doc = self.create_new_document(agent_repository_url)
#					print agent_repository_url


	def import_doc(self, doc):
		(download_status, file) = common.download_file(doc.agent_repository_url)
		if download_status == STATE_OK:
			return (STATE_OK, file)
		else:
			return (download_status, file)

class AgentDoba(AgentGeneral):
	AGENT_NAME = "DOBA"
	BASE_URL = "http://www.doba.si/"
	JSON_TEMPLATE = {"school": "DOBA Maribor"}

agent_base.add_agent(AgentDoba())

	