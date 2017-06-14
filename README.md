DataStalker
============

Project status: Work in progress!

Conceptually based on the WifiStalker but simplified. 
- Gather packets from one of few sources (802.11 monitoring, ethernet packet sniffing),
- decorate them with metadata,
- store for analysis in one or many databases.


Pipeline
============

Data is read and converted using a simple linear pipeline - which connects one
or more stages. For example:

  [Wifi Sniffer] -> [Beacon filter] -> [Geolocalization] -> [Elastic Search]

Wifi Sniffer is a "source stage" which produces initial data. This data is later
filtered and decorated with two other stages, to be finally stored in the
Elastic Search database by the last stage.

So... it's mostly wifistalker split into stages so that I can do metadata
analysis using Kibana&Elasticsearch (or Splunk with correct storing stage). Kind
of like logstash for wifi/bt metadata.

Usage
============

1. Define a pipeline in a single YAML file. 

```yaml
log_level: DEBUG
log_file: null

# Construct a pipeline to handle logged data
pipeline:
  - wifi_sniffer:
      name: 'main'
      interface: wlan0mon
      related_interface: null

      # Enable hopping:
      hopper:

        max_karma: 10
        channels: [
          # 2.4 GHz
          1,6,11, 3,8,13, 2,7,12, 4,10,5,9,
          # 5 GHz
          # 36, 40, 44, 48
        ]
        hop_tries: 10

  - beacon_filter:
      cleanup_interval: 600
      max_str_deviation: 5
      max_time_between: 120

  - limit:
      seconds: 6000
      # entries: 600

  - print

  - elasticsearch:
      hostname: '127.0.0.1'
      index: 'ds-{year:04}{month:02}{day:02}'
      port: 9200
```

2. Run: 

  ./stalk --run

3. ???

4. Profit
