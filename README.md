DataStalker
============

Project status: Basic setups work. I use it for presence detection in home made
alarm system.

Conceptually this project is based on the WifiStalker but is simplified
according to the "Unix philosophy" - do one thing and do it well.

- Gather packets from one of few sources (802.11 monitoring, ethernet packet
  sniffing),
- Decorate them with metadata,
- store for analysis in one or many databases.


Pipeline
============

Data is read and converted using a simple linear pipeline - which connects one
or more stages. Stages pass between them "messages" which represent packets or
events. 

Example:

  [Wifi Sniffer] -> [Beacon filter] -> [OUI decoder] -> [ElasticSearch]

Wifi Sniffer is a "source stage" which produces initial data. This data is later
filtered and decorated with two other stages, to be finally stored in the
ElasticSearch database by the last stage.

This approach allows to freely design pipeline stages and do analysis outside
using ELK stack. It's relatively painless to add new stage. 

Usage
============

1. Define a pipeline in a single YAML file - see a config.template.yml for
   an example.

2. Run: 
  ./stalk --run -c config.yaml

3. ???

4. Profit

