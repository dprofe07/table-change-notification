import json
import re
import sys
import threading
import argparse
import time

import gspread

from spectator import *

with open('tables.json', encoding='utf-8') as f:
    data = json.load(f)

aparser = argparse.ArgumentParser()

aparser.add_argument('table', choices=data.keys())
aparser.add_argument('name')
aparser.add_argument('--gui-text', action='store_true')
aparser.add_argument('--show-table-link', action='store_true')

args = aparser.parse_args(sys.argv[1:])

if args.show_table_link:
    print(f'Table link: https://docs.google.com/spreadsheets/d/{data[args.table]["table-key"]}')

gc = gspread.oauth(credentials_filename='client_secret.json')
spec = Spectator(gc, args.name, prepare_dict(data[args.table], data['default']), args.gui_text)

threading.Thread(target=spec.mainloop).start()
if spec.tasks_fetcher is not None:
    spec.tasks_fetcher.tk.mainloop()
