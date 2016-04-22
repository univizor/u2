
from document.models import Document
from document.states import *
from django.utils import timezone

import logging
logger = logging.getLogger('u2.agent_base')


agents = []

def add_agent(agent):
    agents.append(agent)

class Agent(object):
    AGENT_NAME = "ABC"
    AGENT_VERSION = 1
    
    def agent_get_existing(self, agent_name, agent_version, agent_repository_url):
            # check if this specific download exists already
            results = Document.objects.filter(agent_name = agent_name,
                                            agent_version = agent_version,
                                            agent_repository_url = agent_repository_url).exclude(agent_state = STATE_IN_PROGRESS)	
                                            # we exclude in progress, as that might be an indicator of previous runs where things went wrong
            if len(results)>0:
                    logger.info("Found existing entry %s %s %s" % (agent_name, agent_version, agent_repository_url))
            return results

    def create_new_document(self, repository_url):
        d = Document()
        dups = self.agent_get_existing(self.AGENT_NAME, self.AGENT_VERSION, repository_url)
        if dups:
                return None
        # to do - Handle IN-PROGRESS dups that are now explicitely not included in agent_get_existing()
        #	d.agent_state = STATE_DUP
        #	d.agent_dup = dups[0]
        #	logger.info("Duplicate found %s - %s" % (thesis_url, dups[0]))
        #	d.save()
        #	continue
        d.agent_name = self.AGENT_NAME
        d.agent_version = self.AGENT_VERSION
        d.agent_repository_url = repository_url
        d.agent_date = timezone.now()
        d.status = STATE_WAITING
        d.save()
        return d
            
				
    def import_catalog(self):
        pass
    def import_doc(self, doc):
        pass