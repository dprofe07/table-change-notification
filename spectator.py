import copy
import re
import time

import gspread
from gspread.utils import rowcol_to_a1

from winotify import Notification

from task_fetcher import TaskFetcher


def notify(text):
    Notification(
        'Table notificator',
        'Изменение в таблице!',
        text,
        'C:\\Users\\dima\\PycharmProjects\\table-change-notification\\spreadsheets.ico'
    ).show()
    print(f'Notify: {text}')


def prepare_dict(selected, base):
    res = copy.deepcopy(base)
    for k in selected.keys():
        if isinstance(selected[k], dict):
            res[k] = prepare_dict(selected[k], res[k])
        else:
            res[k] = selected[k]
    return res



class Spectator:
    def __init__(self, gc, person_name, data: dict, gui_text: bool):
        self.gc = gc
        self.table_key = data['table-key']
        self.tasks_row = data.get('tasks-row')
        self.worksheet_picking_type = data['worksheet']
        self.task_number_type = data['task-number']
        self.statuses = data['statuses']
        self.first_task_column = data['first-task-column']
        self.previous_task_marks = None
        self.tasks_fetcher = TaskFetcher(data['tasks-url']) if data.get('tasks-url') and gui_text else None

        self.stopped = False
        self.worksheet: gspread.Worksheet = None
        self.tasks_numbers: list[str] | None = None
        self.load_worksheet()

        self.person_number = self.find_person_number(person_name, data['names-column'])

    def load_worksheet(self):
        self.worksheet = self.choose_worksheet(self.gc.open_by_key(self.table_key).worksheets(True))
        print(f'Loaded worksheet: {self.worksheet.title}')

        self.tasks_numbers = [it.value for it in self.worksheet.range(
            rowcol_to_a1(self.tasks_row, self.first_task_column) + ':' +
            rowcol_to_a1(self.tasks_row, self.worksheet.col_count)
        )] if self.tasks_row is not None else None

    def on_got_marks(self, new_data):
        if self.previous_task_marks is None:
            print('First load succeed')
            self.previous_task_marks = new_data
        elif new_data != self.previous_task_marks:
            if len(new_data) != len(self.previous_task_marks):
                while len(new_data) < len(self.previous_task_marks):
                    new_data.append('')
                while len(new_data) > len(self.previous_task_marks):
                    self.previous_task_marks.append('')

            for i, (it, pit) in enumerate(zip(new_data, self.previous_task_marks)):
                if it != pit:
                    self.on_delta(i, pit, it)
            self.previous_task_marks = new_data


    def get_number_str(self, number):
        if self.task_number_type == '$task-row':
            if self.tasks_numbers is None:
                raise ValueError("tasks_numbers is None")
            return self.tasks_numbers[number]
        else:
            return str(number)

    def on_delta(self, number, was, now):
        txt = self.statuses.get(now)
        if txt:
            notify(f'Задача {self.get_number_str(number)} {txt}')
        else:
            notify(f'Невалидное значение в задаче {self.get_number_str(number)}: было `{was}`, теперь `{now}`')

        if txt == 'выдана' and self.tasks_fetcher:
            q = self.get_number_str(number)
            self.tasks_fetcher.show_task(int(q) if q.isdigit() else number)

    def choose_worksheet(self, worksheets):
        if self.worksheet_picking_type == '$D_number':
            sheet_hws = [it for it in worksheets if it.title.startswith('Д') and it.title[1:].isdigit()]
            sheet_hws.sort(key=lambda it: int(it.title[1:]))
            return sheet_hws[-1]
        elif self.worksheet_picking_type == '$first':
            return worksheets[0]
        else:
            return ([it for it in worksheets if it.title == self.worksheet_picking_type] or [None])[0]


    def find_person_number(self, name, names_column) -> int:
        for i, it in enumerate(self.worksheet.col_values(names_column)):
            if name in it:
                print(f'Found name {it} at {i + 1}')
                return i + 1
        return -1

    def stop(self):
        self.stopped = True

    def mainloop(self):
        t = 0
        print('Starting loop')
        while not self.stopped:
            range_ = rowcol_to_a1(self.person_number,  self.first_task_column) + ':' + rowcol_to_a1(self.person_number, self.worksheet.col_count)
            data = self.worksheet.get(range_)
            self.on_got_marks(data[0])
            time.sleep(1)
            t += 1
            if t % 100 == 0:
                self.load_worksheet()