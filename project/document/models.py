from __future__ import unicode_literals


import json
import shutil
import os
import datetime
from django.db import models
from django.conf import settings
from django.forms.models import model_to_dict

import logging
logger = logging.getLogger('u2.document.model')

from aws import awslib

# Create your models here.

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, datetime.datetime):
        serial = obj.isoformat()
        return serial
    raise TypeError ("Type not serializable")


from states import * # STATE_OK, STATE_WAITING, STATE_IN_PROGRESS, STATE_PERM_FAIL, STATE_TEMP_FAIL, STATE_DUP
STATES = (	(STATE_OK, 'success'), 
                (STATE_WAITING, 'waiting'), 
                (STATE_IN_PROGRESS, 'in-progress'),
                (STATE_PERM_FAIL, 'permanent fail'), 
                (STATE_TEMP_FAIL, 'temporary fail'), 
                (STATE_DUP, 'duplicate'),
                )

# Each document goes through four stages
# download -> pdf2txt -> cleantxt -> index
# For the sake of simplicity, all four stages are presented in a single model


class Document(models.Model):
	document_dir_url = models.CharField(max_length=500)
	
	# downloading agent data
	agent_name = models.CharField(max_length=30)		# ex. "FRI"
	agent_version = models.IntegerField(null=False)			# ex. 1
	agent_repository_url = models.CharField(max_length=500, null=False)		# ex "2313"	# this id should be enough to redownload easily, can be the same as url
	agent_date = models.DateTimeField('date downloaded')
	agent_json_data = models.TextField()
	agent_state = models.IntegerField(choices=STATES, default=STATE_WAITING)
	agent_md5hash = models.CharField(max_length=36)		
	agent_dup = models.ForeignKey('Document', default=None, related_name='agentdup', null=True)

	#pdf2txt data
	pdf2txt_version = models.IntegerField(null=True)	# null means not reached yet
	pdf2txt_state = models.IntegerField(choices=STATES, default=STATE_WAITING)
	pdf2txt_date = models.DateTimeField('date converted', null=True)
	pdf2txt_md5hash = models.CharField(max_length=36)		
	pdf2txt_dup = models.ForeignKey('Document', default=None, related_name='pdfdup', null=True)

	#clean data
	cleantxt_version = models.IntegerField(null=True)	# null means not reached yet
	cleantxt_state = models.IntegerField(choices=STATES, default=STATE_WAITING)
	cleantxt_date = models.DateTimeField('date cleaned', null=True)
	cleantxt_md5hash = models.CharField(max_length=36)		

	#index data
	index_version = models.IntegerField(null=True)		# null means not reached yet
	index_state = models.IntegerField(choices=STATES, default=1)
	index_date = models.DateTimeField('date cleaned', null=True)
		  
	 
	def delete(self):
		raise Exception("Not yet implemnted")
		# should delete everything on S3
		pass
	
	def get_self_id(self):
		# problem: we're using db-specific data through self.id... should we?
		return str(self.id)
	
	def get_document_dir_url(self):
		# we could hash repository urls...
		if not self.id:	
			raise Exception("Document must first be saved")
		return settings.S3_HOME + "/" + self.agent_name + "-" + str(self.agent_version)	+ "-"  + self.get_self_id()
	
	def get_s3_dir(self):
		return self.agent_name + "-" + str(self.agent_version) + "/" + self.get_self_id()
		
        def get_s3_pdf_file_name(self):
                return self.get_s3_dir() + "/input.pdf"

        def get_s3_pdf2txt_file_name(self):
                return self.get_s3_dir() + "/raw.txt"

        def get_s3_cleantxt_file_name(self):
                return self.get_s3_dir() + "/clean.txt"
		
	def get_local_dir(self):
		return settings.LOCAL_TMP +"/" + self.get_s3_dir()

        def get_local_pdf_file_name(self):
                return self.get_local_dir() + "/input.pdf"        

        def get_local_pdf2txt_file_name(self):
                return self.get_local_dir() + "/raw.txt"        

        def get_local_cleantxt_file_name(self):
                return self.get_local_dir() + "/clean.txt"        

        def make_local_dir(self):
		local_dir = self.get_local_dir()
		if not os.path.exists(local_dir):
		    os.makedirs(local_dir)

	# agent specific functions
	
	def agent_get_existing(self, agent_name, agent_version, agent_repository_url):
		# check if this specific download exists already
		results = Document.objects.filter(agent_name = agent_name,
						agent_version = agent_version,
						agent_repository_url = agent_repository_url).exclude(agent_state = STATE_IN_PROGRESS)	
                                                # we exclude in progress, as that might be an indicator of previous runs where things went wrong
		if len(results)>0:
			logger.info("Found existing entry %s %s %s" % (agent_name, agent_version, agent_repository_url))
		return results

	def upload_pdf_file(self, file):
		bucket = awslib.get_s3_bucket()
		file_name = self.get_s3_pdf_file_name()
		key = bucket.new_key(file_name)
		logger.info("Uploading to s3: %s" % file_name)	
		file.seek(0)
		key.set_contents_from_file(file)
		
		# now also save into tmp local dir
		file.seek(0)		
		self.make_local_dir()
		destfile = open(self.get_local_pdf_file_name(), "w+")
		shutil.copyfileobj(file, destfile)
		

	def upload_pdf2txt(self):
		bucket = awslib.get_s3_bucket()
		file_name = self.get_local_pdf2txt_file_name()
		key = bucket.new_key(self.get_local_pdf2txt_file_name())
		logger.info("Uploading to s3: %s" % file_name)	
		key.set_contents_from_filename(file_name)

	def upload_cleantxt(self):
		bucket = awslib.get_s3_bucket()
		file_name = self.get_local_cleantxt_file_name()
		key = bucket.new_key(self.get_local_cleantxt_file_name())
		logger.info("Uploading to s3: %s" % file_name)	
		key.set_contents_from_filename(file_name)
		

	def download_to_local_pdf(self):
		# downloads the file and makes it locally reachable, if the cached version already exists, so much better
		# returns file name
		self.make_local_dir()
		local_file_name = self.get_local_pdf_file_name()
		if not os.path.exists(local_file_name):
			logger.debug("Downloading to local cache %s" % local_file_name)	
			awslib.s3_to_local_file(self.get_s3_pdf_file_name(), local_file_name)
		else:
			logger.debug("File already cached locally %s" % local_file_name)	
		return local_file_name

	def download_to_local_pdf2txt(self):
		# downloads the file and makes it locally reachable, if the cached version already exists, so much better
		# returns file name
		self.make_local_dir()
		local_file_name = self.get_local_pdf2txt_file_name()
#		print local_file_name, self.get_s3_pdf2txt_file_name()
		if not os.path.exists(local_file_name):
			logger.debug("Downloading to local cache %s" % local_file_name)	
			awslib.s3_to_local_file(self.get_s3_pdf2txt_file_name(), local_file_name)
		else:
			logger.debug("File already cached locally %s" % local_file_name)	
		return local_file_name

	def download_to_local_cleantxt(self):
		# downloads the file and makes it locally reachable, if the cached version already exists, so much better
		# returns file name
		self.make_local_dir()
		local_file_name = self.get_local_cleantxt_file_name()
#		print local_file_name, self.get_s3_pdf2txt_file_name()
		if not os.path.exists(local_file_name):
			logger.debug("Downloading to local cache %s" % local_file_name)	
			awslib.s3_to_local_file(self.get_s3_cleantxt_file_name(), local_file_name)
		else:
			logger.debug("File already cached locally %s" % local_file_name)	
		return local_file_name
		
        def save(self, *args, **kwargs):
                # Helps with debugging if latest model is simply saved as sql
                self.make_local_dir()
                f = open(self.get_local_dir() + "/sqldump.txt", "w+")
                print >>f, json.dumps(model_to_dict(self), indent=8, default=json_serial)
                super(Document, self).save(*args, **kwargs)
                        


