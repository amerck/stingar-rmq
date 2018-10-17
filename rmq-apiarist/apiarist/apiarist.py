import os
import sys
import argparse
from ConfigParser import ConfigParser
from multiprocessing import Process

from amqp_receiver import AMQPReceiver
from storage import StingarDB
from normalizer import Normalizer


def parse_config(config_file):
    if not os.path.isfile(config_file):
        sys.exit("Could not find configuration file: {0}".format(config_file))

    parser = ConfigParser()
    parser.read(config_file)

    config = dict()
    config['mongo_host'] = parser.get('mongodb', 'mongo_host')
    config['mongo_port'] = parser.getint('mongodb', 'mongo_port')
    config['mongo_db'] = parser.get('mongodb', 'mongo_database')

    config['amqp_host'] = parser.get('rabbitmq', 'amqp_host')
    config['amqp_username'] = parser.get('rabbitmq', 'amqp_username')
    config['amqp_password'] = parser.get('rabbitmq', 'amqp_password')

    return config


def main():
    parser = argparse.ArgumentParser(description='Apiarist')
    parser.add_argument("--config", dest="config_file", default="apiarist.cfg")
    parser.add_argument("--rabbitmq", action='store_true', default=False)
    parser.add_argument("--normalizer", action='store_true', default=False)

    args = parser.parse_args()
    c = parse_config(args.config_file)

    db = StingarDB(host=c['mongo_host'], port=c['mongo_port'], db_name=c['mongo_db'])

    procs = []
    if args.rabbitmq:
        server = AMQPReceiver(db, c['amqp_username'], c['amqp_password'], host=c['amqp_host'])
        print(" [x] Starting AMQP handler")
        p = Process(target=server.run)
        p.start()
        procs.append(p)

    if args.normalizer:
        print("[x] Starting normalizer")
        normalizer = Normalizer(db, ignore_rfc1918=False)
        p = Process(target=normalizer.start_processing)
        p.start()
        procs.append(p)

    for p in procs:
        p.join()


if __name__ == "__main__":
    main()
