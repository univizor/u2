import os, sys
import subprocess

import pysolr
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


from django.utils import timezone

from document.models import Document
from document.states import *


INDEX_VERSION = 9
def extract_all():
	docs1 = Document.objects.filter(cleantxt_state = STATE_OK, index_state__in = [STATE_WAITING, STATE_IN_PROGRESS])
	docs2 = Document.objects.filter(cleantxt_state = STATE_OK, index_state__in = [STATE_OK], index_version__lt = INDEX_VERSION)
	docs = list(docs1) + list(docs2)
	logger.info("Running cleantxt on %i documents" % len(docs))
	solr = pysolr.Solr('http://localhost:8983/solr/u2core/')		
	for doc in docs:
		cleantxt_file_name = doc.download_to_local_cleantxt()
		doc.index_version = INDEX_VERSION
		doc.index_state = STATE_IN_PROGRESS
		doc.index_date = timezone.now()
		doc.save()
		content = open(cleantxt_file_name, "r").read().decode("utf-8")
		solrdoc = {'id': str(doc.id), 
			'cleantxt': content}
			
		solr.add([solrdoc])
		logger.info("Successfully done indexing txt on %s" % (cleantxt_file_name))
		doc.index_state = STATE_OK
		doc.save()
					
					     
					     
if __name__ == "__main__":
	extract_all()
	
	