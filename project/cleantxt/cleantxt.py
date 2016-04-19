import os, sys
import subprocess

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

import cleaner

CLEANTXT_VERSION = 8
def extract_all():
	docs1 = Document.objects.filter(pdf2txt_state = STATE_OK, cleantxt_state__in = [STATE_WAITING, STATE_IN_PROGRESS])
	docs2 = Document.objects.filter(pdf2txt_state = STATE_OK, cleantxt_state__in = [STATE_OK], cleantxt_version__lt = CLEANTXT_VERSION)
	docs = list(docs1) + list(docs2)
	logger.info("Running cleantxt on %i documents" % len(docs))
	for doc in docs:
		pdf2txt_file_name = doc.download_to_local_pdf2txt()
		cleantxt_file_name = doc.get_local_cleantxt_file_name()
		doc.cleantxt_version = CLEANTXT_VERSION
		doc.cleantxt_state = STATE_IN_PROGRESS
		doc.cleantxt_date = timezone.now()
		doc.save()
		content = open(pdf2txt_file_name, "r").read()
		content = cleaner.get_cleaned(content)
		f = open(cleantxt_file_name, "w")
		f.write(content)
		f.close()
		doc.upload_cleantxt()
		logger.info("Successfully done cleaning txt on %s to %s" % (pdf2txt_file_name, cleantxt_file_name))
		doc.cleantxt_state = STATE_OK
		doc.save()
					
					     
					     
if __name__ == "__main__":
	extract_all()
	
	