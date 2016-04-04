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

from statuses import *
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
			d.agent_name = AGENT_NAME
			d.agent_version = AGENT_VERSION
			d.agent_repository_url = thesis_url
			d.agent_date = timezone.now()
			dups = d.agent_get_existing()
			if dups:
				d.agent_state = STATUS_DUP
				d.agent_dup = dups[0]
				logger.info("Duplicate found %s - %s" % (thesis_url, dups[0]))
				d.save()
				continue
			d.status = STATUS_IN_PROGRESS
			d.save()
			d.json = copy.copy(JSON_TEMPLATE)
			(status, local_file) = eprints.download_page(thesis_url, d.json)
			if status == STATUS_PERM_FAIL:
				d.status = STATUS_PERM_FAIL
				logger.info("Permanent fail %s" % thesis_url)
				d.save()
				continue
                        d.agent_json_data = json.dumps(d.json)
			logger.info("Success: %s" % (thesis_url))
			print d.agent_name, d.agent_version, d.agent_repository_url
			d.agent_state = STATUS_OK
			d.save()


if __name__ == "__main__":
	extract_all()