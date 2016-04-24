import json
import logging
import copy
import datetime
import requests
import bs4

logger = logging.getLogger('u2.agent_bio')

URL_BASE = 'http://www.ffa.uni-lj.si/'
URL_START = URL_BASE + 'knjiznica/diplome-magisteriji-in-doktorati/'

from document.states import *
import eprints
JSON_TEMPLATE = {"school": "Biotehniska fakulteta"}
import common


import agent_base

TOPURLS = [	'http://www.digitalna-knjiznica.bf.uni-lj.si/biologija.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/gozdarstvo.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/agronomija.htm', 
		'http://www.digitalna-knjiznica.bf.uni-lj.si/zootehnika.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/krajinska-arhitektura.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/lesarstvo.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/mikrobiologija.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/zivilstvo.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/biotehnologija.htm',
		'http://www.digitalna-knjiznica.bf.uni-lj.si/podiplomski_studij.htm'
	]

def stripall(s):
	s = s.replace("\t", "")
	s = s.replace("\n", "")
	s = s.replace("\r", "")
	s = s.replace(" ", "")
	return s
class Agent(agent_base.Agent):
	AGENT_NAME = "BIO"
	AGENT_VERSION = 1

	def import_catalog(self):
		for top_url in TOPURLS:
			logger.info('Scraping %s' % top_url)
			response = common.requests_get_retry(top_url)
			url_list = set()
			soup = bs4.BeautifulSoup(response.content, "html.parser")
			common.bs_make_links_absolute(soup, URL_BASE)
			jdata = copy.copy(JSON_TEMPLATE)

			for item in soup.select('tr'):
				l = item.select('td')
				alist = item.select('a')
				if alist:
					agent_repostiory_url = None
					for node in alist:
						agent_repository_url = node.attrs.get('href')
						if agent_repository_url:
							break
				else:
					continue # row headers only
				if len(l) == 5:
					jdata['author'] = stripall(l[0].text)
					jdata['mentor'] = stripall(l[1].text)
					jdata['title'] = stripall(l[2].text)
					jdata['top_url'] = top_url
				elif len(l) == 4:
					# gozdarstvio
					jdata['author'] = stripall(l[0].text)
					jdata['title'] = stripall(l[1].text)
				elif len(l) == 4:
					# lesarstvo
					# gozdarstvio
					jdata['author'] = stripall(l[0].text)
					jdata['title'] = stripall(l[2].text)
					
#				print jdata, agent_repository_url
				doc = self.create_new_document(agent_repository_url, jdata)
	
	def import_doc(self, doc):
		(state, file) = common.download_file(doc.agent_repository_url)
		return (state, file)

agent_base.add_agent(Agent())

	