from ness.commands import build_database
from ness.commands import build_model
from ness.commands import search
from argparse import ArgumentParser
import multiprocessing as mp
import tempfile
import os

argument_parser = ArgumentParser()
argument_parser.add_argument('--version', action='store_true')
argument_subparsers = argument_parser.add_subparsers()

build_model_subparser = argument_subparsers.add_parser("build_model", help="Build a sequence vectorization model")
build_model_subparser.add_argument('--input', help="input file in FASTA format", required=True)
build_model_subparser.add_argument('--output', required=True)
build_model_subparser.add_argument('--model-type', choices=['word2vec'], default='word2vec')
build_model_subparser.add_argument('--vector-size', type=int, default=100)
build_model_subparser.add_argument('--window-size', type=int, default=25)
build_model_subparser.add_argument('--min-count', type=int, default=1)
build_model_subparser.add_argument('--ksize', type=int, default=3)
build_model_subparser.add_argument('--threads', type=int, default=mp.cpu_count())
build_model_subparser.add_argument('--epochs', type=int, default=3)
build_model_subparser.add_argument('--corpus-file', type=str, default=os.path.join(tempfile.TemporaryDirectory().name, 'corpus.txt'))
build_model_subparser.add_argument('--both-strands', action='store_true', default=False)
build_model_subparser.add_argument('--debug', action="store_true", default=False)
build_model_subparser.set_defaults(func=build_model)

build_database_subparser = argument_subparsers.add_parser("build_database")
build_database_subparser.add_argument('--input', required=True)
build_database_subparser.add_argument('--output', required=True)
build_database_subparser.add_argument('--model', required=True)
build_database_subparser.add_argument('--database-type', choices=['scann'], default='scann')
build_database_subparser.add_argument('--chunksize', default=100000, type=int)
build_database_subparser.add_argument('--slicesize', default=None, type=int)
build_database_subparser.add_argument('--jumpsize', default=None, type=int)
build_database_subparser.add_argument('--both-strands', action='store_true', default=False)
build_database_subparser.add_argument('--debug', action="store_true", default=False)
build_database_subparser.set_defaults(func=build_database)

search_subparser = argument_subparsers.add_parser("search")
search_subparser.add_argument('--input', required=True)
search_subparser.add_argument('--output', required=True)
search_subparser.add_argument('--database', required=True)
search_subparser.add_argument('--debug', action="store_true", default=False)
search_subparser.add_argument('--hits', default=10, type=int)
search_subparser.add_argument('--chunksize', default=10000, type=int)
search_subparser.add_argument('--threads', default=mp.cpu_count(), type=int)
search_subparser.add_argument('--scann-mode', default='ah', choices=['ah', 'brute_force'])
search_subparser.set_defaults(func=search)