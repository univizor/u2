from __future__ import unicode_literals

from django.db import models
from django.conf import settings

import logging
logger = logging.getLogger('u2.agent_fri')

# Create your models here.

STATES = ((0, 'success'), (1, 'in-progress'), (2, 'permanent fail'), (3, 'duplicate'))

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
	agent_state = models.IntegerField(choices=STATES, default=1)
	agent_md5hash = models.CharField(max_length=36)		
	agent_dup = models.ForeignKey('Document', default=None, related_name='agentdup', null=True)

	#pdf2txt data
	pdf2txt_version = models.IntegerField(null=True)	# null means not reached yet
	pdf2txt_state = models.IntegerField(choices=STATES, default=1)
	pdf2txt_date = models.DateTimeField('date converted', null=True)
	pdf2txt_md5hash = models.CharField(max_length=36)		
	pdf2txt_dup = models.ForeignKey('Document', default=None, related_name='pdfdup', null=True)

	#clean data
	cleantxt_version = models.IntegerField(null=True)	# null means not reached yet
	cleantxt_state = models.IntegerField(choices=STATES, default=1)
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
	
	def get_document_dir_url(self):
		# problem: we're using db-specific data through self.id... should we?
		# we could hash repository urls...
		if not self.id:	
			raise Exception("Document must first be saved")
		return settings.S3_HOME + "/" + self.agent_name + "-" + str(self.agent_version)	+ "-"  + str(self.id)
	
	def agent_get_existing(self):
		# check if this specific download exists already
		results = Document.objects.filter(agent_name = self.agent_name,
						agent_version = self.agent_version,
						agent_repository_url = self.agent_repository_url,
						)#agent_state__in = (0,2,3,4))
		if len(results)>0:
			logger.info("Found existing entry %s %s %s" % (self.agent_name, self.agent_version, self.agent_repository_url))
		return results

