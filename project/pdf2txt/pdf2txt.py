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

PDF2TXT_VERSION = 6
def extract_all():
	docs1 = Document.objects.filter(agent_state = STATE_OK, pdf2txt_state__in = [STATE_WAITING, STATE_IN_PROGRESS])
	docs2 = Document.objects.filter(agent_state = STATE_OK, pdf2txt_state__in = [STATE_OK], pdf2txt_version__lt = PDF2TXT_VERSION)
	docs = list(docs1) + list(docs2)
	logger.info("Running pdf2txt on %i documents" % len(docs))
	for doc in docs:
		pdf_file_name = doc.download_to_local_pdf()
		pdf2txt_file_name = doc.get_local_pdf2txt_file_name()
		doc.pdf2txt_version = PDF2TXT_VERSION
		doc.pdf2txt_state = STATE_IN_PROGRESS
		doc.pdf2txt_date = timezone.now()
		doc.save()
		try:
			subprocess.check_call(["pdftotext", 
						"-enc", "UTF-8",
						pdf_file_name,
						pdf2txt_file_name])
		except subprocess.CalledProcessError as e:
			logger.error("Failed to run pdftotext on %s" % pdf_file_name)
			doc.pdf2txt_state = STATE_PERM_FAIL
			doc.save()
			continue
		logger.info("Successfully done pdftotext on %s to %s" % (pdf_file_name, pdf2txt_file_name))
		doc.upload_pdf2txt()
		doc.pdf2txt_state = STATE_OK
		doc.save()
					
					     
					     
if __name__ == "__main__":
	extract_all()
	
	