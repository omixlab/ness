#!/usr/bin/env python

from ness.cli.arguments import argument_parser
import logging

if __name__ == '__main__':
    
    arguments = argument_parser.parse_args()
    
    if hasattr(arguments, 'debug') and arguments.debug:
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    if hasattr(arguments, 'func'):
        arguments.func(arguments)
    else:
        argument_parser.print_help()
