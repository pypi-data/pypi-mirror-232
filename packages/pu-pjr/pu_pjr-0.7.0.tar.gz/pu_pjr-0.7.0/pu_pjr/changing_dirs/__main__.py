import argparse

from . import quickcd
from . import utils

def main():
    parser = argparse.ArgumentParser(
        prog='quickcd',
        description='Change directories quickly'
    )

    # Sub-parser
    subparser = parser.add_subparsers()

    # Sub-parser for the "add" command
    add_parser = subparser.add_parser(
        'add', help='Add a new entry'
    )
    add_parser.set_defaults(which='add')

    add_parser.add_argument(
        'name', type=str, help='The name of the entry'
    )
    add_parser.add_argument(
        '--path', '-p', type=str, 
        help='The path of the entry, if none' + 
             ' is specified the current working directory is used',
        required=False
    )

    # Sub-parser for the "remove" command
    remove_parser = subparser.add_parser(
        'remove', help='Remove an entry'
    )
    remove_parser.set_defaults(which='remove')

    remove_parser.add_argument(
        'name', type=str, help='The name of the entry'
    )

    # Sub-parser for the "list" command
    list_parser = subparser.add_parser(
        'list', help='List all the entries'
    )
    list_parser.set_defaults(which='list')

    # Sub-parser for the "change" command
    change_parser = subparser.add_parser(
        'change', help='Change to an entry'
    )
    change_parser.set_defaults(which='change')

    change_parser.add_argument(
        'name', type=str, help='The name of the entry'
    )

    args = parser.parse_args()

    if args.which == 'add':
        if args.path is None:
            args.path = utils.get_cwd()

        adding = quickcd.add_entry(args.name, args.path)
        if not adding:
            print(f'Entry "{args.name}" already exists')
        else:
            print(f'Entry "{args.name}" added')
    elif args.which == 'remove':
        removing = quickcd.remove_entry(args.name)
        if not removing:
            print(f'Entry "{args.name}" does not exist')
        else:
            print(f'Entry "{args.name}" removed')
    elif args.which == 'list':
        entries = quickcd.list_entries()
        if len(entries) == 0:
            print('No entries found')
        else:
            for name, path in entries.items():
                print(f'{name}: {path}')
    elif args.which == 'change':
        changing = quickcd.change_to_entry(args.name)
        if not changing:
            print(f'Entry "{args.name}" does not exist')
        else:
            print(f'Changed to entry "{args.name}"')

if __name__ == "__main__":
    main()