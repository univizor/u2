import logging
import copy
import datetime
logger = logging.getLogger('u2.agent_fri')

YEARS = [1990, 1994, 1995, 1997, 1998] + range(2000, datetime.date.today().year)

#from document.states import *
import eprints
JSON_TEMPLATE = {"school": "Fakulteta za gradbenistvo in geodezijo"}

import agent_base
class AgentFri(agent_base.Agent):
	AGENT_NAME = "FGG"
	AGENT_VERSION = 1

	def import_catalog(self):
		for year in YEARS:
			logger.info("Scrapping year " + str(year))
			for repository_url in eprints.get_url_list(year, 'http://drugg.fgg.uni-lj.si/'):
				doc = self.create_new_document(repository_url)
	
	def import_doc(self, doc):
		doc.json = copy.copy(JSON_TEMPLATE)
		(status, file) = eprints.download_page(doc.agent_repository_url, doc.json)
		return (status, file)

agent_base.add_agent(AgentFri())

	