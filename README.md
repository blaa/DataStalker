DataStalker
============

This project sniffs metadata from wireless 802.11 networks, decorates them with
more metadata and stores them for later analysis (elasticsearch, CSV, possibly
other) or generates actions in real-time. It creates a pipeline of configurable
stages. Initial stage creates messages which pass through the pipeline. You can
think of it as a "lightweight and hackable logstash".

Datastalker is based on my previous side project - WifiStalker - but is
simplified according to the "Unix philosophy" - do one thing and do it well.

Project status: Basic setups work. I use it for presence detection in home made
alarm system.

Architecture
============
Data is represented by a "Message" class with a standard key-value interface,
which can further by expanded by stages - for e.g. Elasticsearch stage
subclasses it to add schema information. Messages can represent anything, from
network packets to high-level events.

Messages are passed through a pipeline, which consists of two or more stages.
Pipeline and stages are configured using a YAML file - so if built-in stages are
sufficient - it's enough to setup a config file to use Datastalker.

Example pipeline:

  [Wifi Sniffer] -> [Beacon filter] -> [OUI decoder] -> [ElasticSearch storage]

Wifi Sniffer is a "source stage" which produces initial data. This data is later
filtered for duplicates, decorated with network card producers (oui) and finally
stored in the ElasticSearch database by the last stage.

This approach allows to freely design pipeline stages and do analysis outside
using the ELK stack. If the built-in stages are insufficient, it should be
trivial to add a new stage.

For debugging purposes the Datastalker aggregates statistics from all the stages
using standard interface

Stage API
============

Example custom stage

    from datastalker.pipeline import Stage

    @Pipeline.register_stage('custom_stage')
    class CustomStage(Stage):
        "My custom stage"

        def __init__(self, stats, parameter):
            self.stats = stats
            self.parameter = parameter

        def handle(self, message):
            self.stats.incr(custom-stage/ignored)
            message['new_key'] = self.parameter
            return message

        @classmethod
        def from_config(cls, config, stats):
            "Create using stage configuration"

            parameter = config.get('parameter', 42)

            stage = CustomStage(stats, parameter)
            return stage

Usage
============

1. Define a pipeline in a single YAML file - see a config.template.yml for
   an example.

2. Run:
  ./stalk --run -c config.yaml

3. ???

4. Profit
