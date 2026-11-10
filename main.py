import argparse
import json
import os
import sys

import gspread

from spectator import Spectator
from table_data import TableData
from notifier import WinNotifier, TgNotifier, NoneNotifier, Notifier, ConsoleNotifier


def create_gc_object():
    return gspread.oauth(
        scopes=['https://www.googleapis.com/auth/spreadsheets'],
        credentials_filename='_data/client_secret.json',
        authorized_user_filename='_data/authed_user.json'
    )


def create_parser(tables):
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
    aparser.add_argument(
        '--notification-type',
        choices=['win', 'tg', 'console'],
        default='$default',
        help='type of notification program will send'
    )
    integer = lambda t: [int, lambda q: '$file'][t == '$file'](t)

    aparser.add_argument(
        '--tg-notification-id',
        default='$file',
        help='id for tg-notification-bot https://t.me/console_notification_bot',
        type=integer,
    )
    aparser.add_argument(
        '--do-not-save-tg-id',
        action='store_true',
        help='forbid saving passed id for tg notification bot',
    )
    aparser.add_argument(
        '--test-notifier',
        action='store_true',
        help='send test notification as program starts',
    )

    return aparser


def choose_notifier(arg_parser, args) -> Notifier:
    chosen = args.notification_type
    saved_tg_id = None
    if os.path.exists('_data/user-data.json'):
        with open('_data/user-data.json', 'r') as f:
            saved_tg_id = json.load(f).get('tg-id')

    match chosen:
        case '$default':
            if args.tg_notification_id != '$file':
                return TgNotifier(args.tg_notification_id)
            else:
                if os.name == 'nt':
                    return WinNotifier()
                else:
                    return ConsoleNotifier() if saved_tg_id is None else TgNotifier(saved_tg_id)
        case 'win':
            if os.name != 'nt':
                print('[WARN] You are not on windows, may be you shouldn\'t use windows notifications...', file=sys.stderr)
            return WinNotifier()
        case 'tg':
            if args.tg_notification_id == '$file' and saved_tg_id is None:
                arg_parser.error(
                    'if you choose tg notification, you should pass --tg-notification-id '
                    'or have it saved in file (it automatically saved unless you pass '
                    '--do-not-save-tg-id)'
                )
            return TgNotifier(args.tg_notification_id if args.tg_notification_id != '$file' else saved_tg_id)
        case 'console':
            return ConsoleNotifier()
        case _:
            assert False

def main():
    with open('_data/tables.json', encoding='utf-8') as f:
        data = json.load(f)

    aparser = create_parser([i for i in data.keys() if i != '$default'])
    args = aparser.parse_args(sys.argv[1:])

    if args.show_table_link:
        print(f'Table link: https://docs.google.com/spreadsheets/d/{data[args.table]["table-key"]}')

    if args.refresh_token:
        print('Removing old token')
        os.remove('_data/authed_user.json')

    notifier = choose_notifier(aparser, args)

    if args.test_notifier:
        notifier.notify('test notification')

    gc = create_gc_object()

    if gc.http_client.auth.expired:
        print('token протух, обновляем!')
        os.remove('_data/authed_user.json')
        gc = create_gc_object()


    spec = Spectator(gc, args.name, TableData(data, args.table), notifier, args.gui_text)
    spec.mainloop()

if __name__ == '__main__':
    main()