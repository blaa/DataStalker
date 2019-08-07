DataStalker
============

Project status: Basic setups work.

Conceptually this project is based on the WifiStalker but is simplified
according to the "Unix philosophy" - do one thing and do it well.

- Gather packets from one of few sources (802.11 monitoring, ethernet packet sniffing),
- decorate them with metadata,
- store for analysis in one or many databases.


Pipeline
============

Data is read and converted using a simple linear pipeline - which connects one
or more stages. For example:

  [Wifi Sniffer] -> [Beacon filter] -> [Geolocalization] -> [ElasticSearch]

Wifi Sniffer is a "source stage" which produces initial data. This data is later
filtered and decorated with two other stages, to be finally stored in the
ElasticSearch database by the last stage.

So... it's mostly wifistalker split into stages so that I can do metadata
analysis using Kibana&Elasticsearch. Kind of like logstash for wifi/bt metadata
and easy hacking.

Usage
============

1. Define a pipeline in a single YAML file - see a config.template.yml for
   an example.

2. Run: 
  ./stalk --run -c config.yaml

3. ???

4. Profit

