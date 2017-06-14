# (C) 2015 - 2017 by Tomasz bla Fortuna
# License: MIT

import sys
import os
import logging
import argparse

import yaml

from datastalker import version
from datastalker.pipeline import Pipeline

# Register stages
from datastalker import wifisniffer

# Install faulthandler if it's available.
try:
    import faulthandler
    import signal
    faulthandler.enable()
    faulthandler.register(signal.SIGUSR1)
except ImportError:
    print("(no faulthandler)")
    pass

def _parse_arguments():
    "Parse command line arguments"

    desc = 'DataStalker - gather, decorate and store metainformation from traffic'
    p = argparse.ArgumentParser(description=desc)
    act = p.add_argument_group('actions')

    act.add_argument("--run", dest="run",
                     action="store_true",
                     help="Run pipeline")

    act.add_argument("--version", dest="version",
                     action="store_true",
                     help="show version/license info")

    p.add_argument("-c", "--config", dest="config",
                   action="store", type=str, default="config.yaml",
                   help="path to the config file")

    args = p.parse_args()
    return p, args


def action_run(args):
    "Run a pipeline"
    try:
        with open(args.config, 'r') as cfg:
            config = yaml.load(cfg)
    except FileNotFoundError:
        print("Unable to find config file (%s). Pass correct path with -c" % args.config)
        return 1

    log_file = config.get('log_file', None)
    log_level = config.get('log_level', None)
    log_map = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        None: logging.INFO,
    }
    log_level = log_map[log_level]

    logging.basicConfig(filename=log_file,
                        level=log_level)

    if 'pipeline' not in config:
        print("Config file doesn't define a pipeline")
        return 1

    pipeline = Pipeline()
    pipeline.build(config['pipeline'])
    pipeline.run()


def action_version(args):
    "Show version/license info"
    from datastalker import version
    print((
        "DataStalker / WifiStalker-ng\n"
        "Curent version:   {0}\n"
        "Project author:   Tomasz bla Fortuna\n"
        "Backend license:  DataStalker - MIT; PythonWiFi LGPL\n"
    ).format(version.VERSION_STRING))


def run():
    "Run DataStalker"
    parser, args = _parse_arguments()

    if args.run:
        ret = action_run(args)
    elif args.version:
        ret = action_version(args)
    else:
        ret = parser.print_help()

    sys.exit(ret)
