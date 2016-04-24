import logging
import copy
import datetime
import requests
import bs4

logger = logging.getLogger('u2.agent_ffa')

URL_BASE = 'http://www.ffa.uni-lj.si/'
URL_START = URL_BASE + 'knjiznica/diplome-magisteriji-in-doktorati/'

from document.states import *
import eprints
JSON_TEMPLATE = {"school": "Fakulteta za farmacijo"}
import common


import agent_base

class Agent(agent_base.Agent):
	AGENT_NAME = "FFA"
	AGENT_VERSION = 1

	def import_catalog(self):
		page_url = URL_START
		while page_url:
			logger.info('Scraping %s' % page_url)
			response = common.requests_get_retry(page_url)
			url_list = set()
			soup = bs4.BeautifulSoup(response_html.content.decode("utf-8"), "html.parser")
			for item in soup.select('.tx_sevenpack-title a'):
				try:
					url_list.add(URL_BASE + item['href'])
				except:
					logger.error('Failed %s' % item)
					pass
			url_next = None
			for item in soup.select('.tx_sevenpack-navi_page_selection a'):
				if item['title'] == 'Naslednja stran':
					url_next = URL_BASE + item['href']
			for url in url_list:
				doc = self.create_new_document(url)
	
	def import_doc(self, doc):
		doc.json = copy.copy(JSON_TEMPLATE)
		json = doc.json
		response = common.requests_get_retry(doc.agent_repository_url)
		soup = bs4.BeautifulSoup(response.content.decode('utf-8'), 'html.parser').select('.tx_sevenpack-single_view')[0]
		for item in soup.select('table.tx_sevenpack-single_item tr'):
			if not item.select('th') or not item.select('td'):
				continue
			key = item.select('th')[0].get_text()
			value = item.select('td')[0].get_text()
			if 'URL do' in key:
				json['url'] = value
			elif 'Naslov:' in key:
				json['title'] = value
			elif 'Leto:' in key:
				json['year'] = value
			elif 'Avtor(ji):' in key:
				json['author'] = value.split(', ')[0]
		
		if 'url' in json:
			(state, file) = common.download_file(json['url'])
			return (state, file)
		else:
			logger.error("Couldn't find the pdf url in %s" % doc.agent_repository_url)
			return (STATE_TEMP_FAIL, None)

agent_base.add_agent(Agent())

	