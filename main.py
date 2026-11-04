import argparse
import json
import os
import sys
from datetime import datetime

import gspread

from spectator import Spectator
from table_data import TableData


def create_gc_object():
    return gspread.oauth(
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        credentials_filename='_data/client_secret.json',
        authorized_user_filename='_data/authed_user.json'
    )


def parse_args(tables):
    aparser = argparse.ArgumentParser()

    aparser.add_argument(
        'table',
        choices=tables,
        help='table which will be tracked',
    )
    aparser.add_argument(
        'name',
        help='name of person who\'s tasks will be tracked',
    )
    aparser.add_argument(
        '--gui-text',
        action='store_true',
        help='When a task given, show a window with it\'s text if possible',
    )
    aparser.add_argument(
        '--show-table-link',
        action='store_true',
        help='Show a link for the table script is tracking for',
    )
    aparser.add_argument(
        '--refresh-token',
        action='store_true',
        help='Refresh oauth token (repeated authentication will be required)',
    )

    args = aparser.parse_args(sys.argv[1:])
    return args


def main():
    with open('_data/tables.json', encoding='utf-8') as f:
        data = json.load(f)

    args = parse_args([i for i in data.keys() if i != '$default'])

    if args.show_table_link:
        print(f'Table link: https://docs.google.com/spreadsheets/d/{data[args.table]["table-key"]}')

    if args.refresh_token:
        os.remove('_data/authed_user.json')

    gc = create_gc_object()
    if gc.expiry < datetime.now():
        os.remove('_data/authed_user.json')
        gc = create_gc_object()


    spec = Spectator(gc, args.name, TableData(data, args.table), args.gui_text)
    spec.mainloop()

if __name__ == '__main__':
    main()