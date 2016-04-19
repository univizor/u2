solr-6.0.0/bin/solr stop
rm -rf data/u2core
solr-6.0.0/bin/solr start -s data
solr-6.0.0/bin/solr create -c u2core
curl -X POST -H 'Content-type:application/json' --data-binary '{
  "add-field":{
     "name":"cleantxt",
     "type":"text_general",
     "stored":true, 
     "indexed":true }
}' http://localhost:8983/solr/u2core/schema

