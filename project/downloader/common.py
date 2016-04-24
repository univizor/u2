import urlparse
import tempfile
import requests
from document.states import *
def requests_get_retry(url, **kwargs):
	r = None
	for retry in xrange(5):
		try:
			r = requests.get(url, **kwargs)
			break
		except:
			pass
	return r


def download_file(url):
	if url.endswith(".mpg"):
		return (STATE_PERM_FAIL, None)
	r = requests_get_retry(url, stream=True)
	if not r:
		return (STATE_TEMP_FAIL, None)
#	try:
#		print r.headers
#		ext = re.findall(r'filename=.*',
#						 r.headers['Content-Disposition'])[0].split('=')[1].split('.')[-1]
#	except:
#		print('Failed url:', url)
#		return (STATE_TEMP_FAIL, None)
	local_file = tempfile.NamedTemporaryFile()
 	local_file.write(r.content)
	return (STATE_OK, local_file)

def bs_make_links_absolute(soup, url):
    for tag in soup.findAll('a', href=True):
        tag['href'] = urlparse.urljoin(url, tag['href'])
