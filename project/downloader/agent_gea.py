import json
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
		URLS = ['http://gea.gea-college.si/diplome/diplomska_dela_vsp_2009.aspx?studij=1',
			'http://gea.gea-college.si/diplome/diplomska_dela_vsp_2009.aspx?studij=4']
		for url in URLS:
			r = common.requests_get_retry(url)
			soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
			formdict = {}
			for item in soup.select("input[type=hidden]"):
				formdict[item['name']] = item['value']
			#print formdict
			for item in soup.select("input[type=image]"):
				name = item['name']
				formdict[name+".x"] = 1
				formdict[name+".y"] = 1
				#print r.content
				print name
				doc = self.create_new_document(url + "#" + name)
				if doc:
					doc.agent_json_data = json.dumps({'dldict': formdict})
					doc.save()

#				print agent_repository_url


	def import_doc(self, doc):
		url = doc.agent_repository_url.split("#")[0]
		r = common.requests_get_retry(doc.agent_repository_url)
		soup = bs4.BeautifulSoup(r.content.decode('utf-8'), "html.parser")
		postdict = json.loads(doc.agent_json_data)['dldict']
		(download_status, file) = common.download_file(url, postdict = postdict)
		if download_status == STATE_OK:
			return (STATE_OK, file)
		else:
			return (download_status, file)

class AgentGea(AgentGeneral):
	AGENT_NAME = "GEA"
	JSON_TEMPLATE = {"school": "Gea College"}

agent_base.add_agent(AgentGea())

	