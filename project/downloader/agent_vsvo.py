#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
class AgentVsvo(agent_base.Agent):
	AGENT_NAME = "VSVO"
	JSON_TEMPLATE = {"school": u"Visoka šola za varstvo okolja"}

	AGENT_VERSION = 1
	def import_catalog(self):
		BASE_URL = "http://www.vsvo.si/images/pdf/"
		url = BASE_URL
		r = common.requests_get_retry(url)
		soup = bs4.BeautifulSoup(r.content, "html.parser")
		for item in soup.select("li a"):
			agent_repository_url = item['href']
			if not agent_repository_url.startswith("http"):
				agent_repository_url = BASE_URL + agent_repository_url
			l = agent_repository_url.lower()
			if not (("diplom" in l) or ("magistr" in l) or ("naloga" in l)):
				# we miss some that should have been there tho..
				continue
			if "naslov" in l or "_red.pdf" in l:
				continue
			if not l.endswith(".pdf"):
				continue
			doc = self.create_new_document(agent_repository_url)


	def import_doc(self, doc):
		(download_status, file) = common.download_file(doc.agent_repository_url)
		return (download_status, file)


agent_base.add_agent(AgentVsvo())

	