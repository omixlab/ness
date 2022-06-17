import logging

def main():

    from ness.cli.arguments import argument_parser
    from ness.logo import logo
    
    arguments = argument_parser.parse_args()
    
    if hasattr(arguments, 'debug') and arguments.debug:
        print(logo)
        logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    if hasattr(arguments, 'func'):
        arguments.func(arguments)

    elif arguments.version:
        from ness.utils.version import get_version
        print(get_version())

    else:
        print(logo)
        argument_parser.print_help()

if __name__ == '__main__':
    main()