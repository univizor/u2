import re
import json
import os
import subprocess

import tempfile
import requests
import bs4
from slugify import slugify

DL_DIR = '/tmp/'
from document.states import *
import common


def get_url_list(y, url_base):
	url_list = set()
	url = '{}view/year/{}.html'.format(url_base, y)
	response = common.requests_get_retry(url)
	if not response:
		raise Exception("Couldn't download index page for year : %s" % y)
	content = response.content.decode('utf-8')
	soup = bs4.BeautifulSoup(content, "html.parser")
	for item in soup.select('.ep_view_page_view_year p'):
		try:
			url = item.select('a')[0]['href']
			if re.match(r'{}\d+/'.format(url_base), url):
				url_list.add(url)
		except:
			pass
	return url_list

def download_page(thesis_url, d):
	pdfurl = None
	response = common.requests_get_retry(thesis_url)
	if not response:
		return (STATE_TEMP_FAIL, None)
	soup = bs4.BeautifulSoup(response.content.decode('utf-8'), "html.parser")


	d['keywords'] = []

	d['title'] = soup.select('h1')[0].get_text()
	for bar in soup.select('.ep_summary_content_main'):
		d['year'] = re.findall(r'[0-9]{4}', bar.get_text())[0]
		break
	
	for author in soup.select('.ep_summary_content .person_name'):
		d['author'] = author.get_text()
		break
	for anchor in soup.select('table td a'):
		dl_text = anchor.get_text()
		if 'Download' in dl_text or 'Prenos' in dl_text:
			pdfurl = anchor['href']
			break
	for row in soup.select('table table tr'):
		if not row.select('th'):
			continue
		row_header = row.select('th')[0].get_text()
		if 'Item Type:' in row_header or 'Tip vnosa:' in row_header or 'Vrsta dela:' in row_header:
			row_content = row.select('td')[0].get_text()
			if 'Thesis' not in row_content and 'Delo' not in row_content and 'sko delo' not in row_content:
				break # lets break
		if 'ne besede:' in row_header or 'Keywords:' in row_header:
			d['keywords'] = [
				elt.encode('utf-8') for elt in row.select('td')[0].get_text().split(', ')
			]
	if not pdfurl:
		return (STATE_PERM_FAIL, None)
	(download_status, file) = common.download_file(pdfurl)
	if download_status == STATE_OK:
		return (STATE_OK, file)
	else:
		return (download_status, file)
	
	
