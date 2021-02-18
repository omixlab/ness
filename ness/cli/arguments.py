from argparse import ArgumentParser

from ness.commands import build_database
from ness.commands import build_model
from ness.commands import search

argument_parser = ArgumentParser()
argument_subparsers = argument_parser.add_subparsers()

build_model_subparser = argument_subparsers.add_parser("build_model")
build_model_subparser.add_argument('--input', required=True)
build_model_subparser.add_argument('--output', required=True)
build_model_subparser.add_argument('--debug', action="store_true", default=False)
build_model_subparser.set_defaults(func=build_model)

build_database_subparser = argument_subparsers.add_parser("build_database")
build_database_subparser.add_argument('--input', required=True)
build_database_subparser.add_argument('--output', required=True)
build_database_subparser.add_argument('--model', required=True)
build_database_subparser.add_argument('--records_per_chunk', default=100000, type=int)
build_database_subparser.add_argument('--debug', action="store_true", default=False)
build_database_subparser.set_defaults(func=build_database)

search_subparser = argument_subparsers.add_parser("search")
search_subparser.add_argument('--input', required=True)
search_subparser.add_argument('--output', required=True)
search_subparser.add_argument('--model', required=True)
search_subparser.add_argument('--database', required=True)
search_subparser.add_argument('--debug', action="store_true", default=False)
search_subparser.add_argument('--hits', default=10, type=int)
search_subparser.set_defaults(func=search)