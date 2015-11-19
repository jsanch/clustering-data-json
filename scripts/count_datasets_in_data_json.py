import json
from argparse import ArgumentParser

parser = ArgumentParser('Cluster Data.json Datasets')

parser.add_argument('filename')

args = parser.parse_args()


with open(args.filename, 'r') as data_file:
    data = json.load(data_file)

    datasets = data['dataset']

    print len(datasets)
