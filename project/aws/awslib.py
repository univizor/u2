from django.conf import settings

import tempfile
import shutil
from boto.s3.connection import S3Connection

def get_s3_bucket():
         conn = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
         bucket = conn.get_bucket(settings.S3_BUCKET)
         return bucket
         	
def s3_to_local_file(key, file_name):
         bucket = get_s3_bucket()
         key = bucket.get_key(key)
         # we use temp file so we don't have half-downloads
         temp_file = tempfile.NamedTemporaryFile()
         key.get_contents_to_filename(temp_file.name)
         shutil.copyfile(temp_file.name, file_name) 
         

         		  