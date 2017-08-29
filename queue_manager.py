#!/usr/bin/python3
from __future__ import division, print_function, unicode_literals
from pymongo import MongoClient
from time import sleep
import argparse

client = MongoClient()
db = client.sacred


def start_experiment(config):
    from train_convnet import ex
    ex.run(config_updates=config)


def check_for_work():
    try:
        queued_run = db.runs.find({'status': 'QUEUED'})[0]
    except IndexError:
        return None
    config = queued_run['config']
    print("Starting an experiment with the following configuration:")
    print(config)
    db.runs.delete_one({'_id': queued_run['_id']})
    start_experiment(config)


def main_loop():
    while True:
        check_for_work()
        sleep(10)


def print_dict(d, indentation=2):
    for key, value in sorted(d.items()):
        if type(value) == dict:
            print(" "*indentation + key + ":")
            print_dict(value, indentation=indentation+2)
        else:
            print(" "*indentation + key + ": " + str(value))


def list_experiments(status='QUEUED'):
    print("These Experiments have the status '" + status + "':")
    for ex in db.runs.find({'status': status}):
        print("Experiment No " + str(ex['_id']))
        print_dict(ex['config'], indentation=2)
        print("----------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manage queued Sacred experiments.\n" +
                                                 "If called without parameters the queue_manager will fetch " +
                                                 "experiments from the database and run them.")
    parser.add_argument('-l', '--list', action='store_true', help="Show the list of queued experiments.")
    parser.add_argument('-c', '--clear', action='store_true', help="Clear the list of queued experiments.")
    args = parser.parse_args()
    if args.clear:
        db.runs.delete_many({'status': 'QUEUED'})
    if args.list:
        list_experiments()
    elif not args.clear:
        main_loop()
