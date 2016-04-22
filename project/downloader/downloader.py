
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
logger = logging.getLogger('u2.manager')

from document.models import Document
from document.states import *

import agent_base
import agent_fri

def print_usage():
    print "Usage:"
    print "manager.py import_catalog [agent_name]\t Imports all known catalogs"
    print "manager.py workers [agent_name]       \t Imports all known catalogs"


def get_agents(agent_name):
    agents = []
    for agent in agent_base.agents:
        if not agent_name or agent_name == agent.AGENT_NAME:
            agents.append(agent)
    return agents

def get_arg_or_empty(n):
    if len(sys.argv) > n:
        return sys.argv[n]
    else:
        return None
        
        
def run_workers(agent):
    docs1 = Document.objects.filter(agent_state__in = [STATE_WAITING, STATE_IN_PROGRESS]).order_by("id")
    docs2 = Document.objects.filter(agent_state__in = [STATE_OK], agent_version__lt = agent.AGENT_VERSION).order_by("id")
    docs = list(docs1) + list(docs2)
    for doc in docs:
        doc.state = STATE_IN_PROGRESS
        doc.save()
        doc.json = {}
        (status, file) = agent.import_doc(doc)
        if status in (STATE_PERM_FAIL, STATE_TEMP_FAIL):
                doc.agent_state = status
                logger.info("Permanent or temporary fail %s" % doc.agent_repository_url)
                doc.save()
                continue
        doc.agent_json_data = json.dumps(doc.json)
        doc.upload_pdf_file(file)
        logger.info("Success: %s %s %s" % (doc.agent_name, doc.agent_version, doc.agent_repository_url))
        doc.agent_state = STATE_OK
        file.close()
        doc.save()

    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_usage()
    elif sys.argv[1] == "import_catalog":
        agents = get_agents(get_arg_or_empty(2))
        for agent in agents:
            agent.import_catalog()
    elif sys.argv[1] == "workers":
        agents = get_agents(get_arg_or_empty(2))
        for agent in agents:
            run_workers(agent)
    else:
        print_usage()	
