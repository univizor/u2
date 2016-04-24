import logging
import copy
import datetime
logger = logging.getLogger('u2.agent_pef')

YEARS = [2000] + range(2002, datetime.date.today().year)

#from document.states import *
import eprints
JSON_TEMPLATE = {"school": "Pedagoska fakulteta"}

import agent_base
class Agent(agent_base.Agent):
	AGENT_NAME = "PEF"
	AGENT_VERSION = 1

	def import_catalog(self):
		for year in YEARS:
			logger.info("Scrapping year " + str(year))
			for repository_url in eprints.get_url_list(year, 'http://pefprints.pef.uni-lj.si/'):
				doc = self.create_new_document(repository_url)
	
	def import_doc(self, doc):
		doc.json = copy.copy(JSON_TEMPLATE)
		(status, file) = eprints.download_page(doc.agent_repository_url, doc.json)
		return (status, file)

agent_base.add_agent(Agent())


	