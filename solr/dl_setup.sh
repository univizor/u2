wget http://www.apache.si/lucene/solr/6.0.0/solr-6.0.0.tgz
tar -xvzf solr-6.0.0.tgz
solr-6.0.0/bin/solr start -s data
solr-6.0.0/bin/solr create -c u2docs
