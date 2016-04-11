import os, sys
import logging
import copy
import json
if __name__ == "__main__":
	os.environ['DJANGO_SETTINGS_MODULE'] = "u2.settings"
	sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../project"))
	sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "../.."))
	from django.conf import settings
	import django
	django.setup()
logger = logging.getLogger('u2.agent_fri')

import datetime
YEARS = range(2003, datetime.date.today().year)
from django.utils import timezone

from document.states import *
import eprints
from document.models import Document


URL_BASE = 'http://eprints.fri.uni-lj.si/'
AGENT_NAME = 'FRI'
AGENT_VERSION = 1
JSON_TEMPLATE = {"school": "Fakulteta za racunalnistvo in informatiko"}

def extract_all():
	for year in YEARS:
		logger.info("Scrapping year " + str(year))
		for thesis_url in eprints.get_url_list(year, URL_BASE):
			d = Document()
			dups = d.agent_get_existing(AGENT_NAME, AGENT_VERSION, thesis_url)
			if dups:
			        continue
                        # to do - Handle IN-PROGRESS dups that are now explicitely not included in agent_get_existing()
			#	d.agent_state = STATE_DUP
			#	d.agent_dup = dups[0]
			#	logger.info("Duplicate found %s - %s" % (thesis_url, dups[0]))
			#	d.save()
			#	continue
			d.agent_name = AGENT_NAME
			d.agent_version = AGENT_VERSION
			d.agent_repository_url = thesis_url
			d.agent_date = timezone.now()
			d.status = STATE_IN_PROGRESS
			d.save()
			d.json = copy.copy(JSON_TEMPLATE)
			(status, file) = eprints.download_page(thesis_url, d.json)
			if status == STATE_PERM_FAIL:
				d.status = STATE_PERM_FAIL
				logger.info("Permanent fail %s" % thesis_url)
				d.save()
				continue
                        d.agent_json_data = json.dumps(d.json)
			d.upload_pdf_file(file)
			logger.info("Success: %s %s %s %s" % (d.agent_name, d.agent_version, d.agent_repository_url, thesis_url))
			d.agent_state = STATE_OK
			file.close()
			d.save()


if __name__ == "__main__":
	extract_all()