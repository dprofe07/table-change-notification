import re
import time

import gspread
from gspread.utils import rowcol_to_a1

from winotify import Notification

def notify(text):
    noti = Notification('table notificator', 'Изменение в таблице!', text)
    noti.show()


class Spectator:
    def __init__(self, gc, table_key, person_name, names_column, first_task_column):
        self.gc = gc
        self.table_key = table_key
        self.stopped = False
        self.worksheet: gspread.Worksheet = None
        self.load_worksheet()

        self.person_number = self.find_person_number(person_name, names_column)
        # self.person_name = person_name
        self.first_task_column = first_task_column
        self.previous_task_marks = []

    def load_worksheet(self):
        self.worksheet = self.choose_worksheet(self.gc.open_by_key(self.table_key).worksheets(True))

    def on_got_marks(self, new_data):
        if self.previous_task_marks is None:
            self.previous_task_marks = new_data
        elif new_data != self.previous_task_marks:
            for i, (it, pit) in enumerate(zip(new_data, self.previous_task_marks)):
                if it != pit:
                    self.on_delta(i + 1, pit, it)
            self.previous_task_marks = new_data

    def on_delta(self, number, was, now):
        print(f'On task {number}, was: {was}, now: {now}')

    def choose_worksheet(self, worksheets):
        return worksheets[0]

    def find_person_number(self, name, names_column) -> int:
        for i, it in enumerate(self.worksheet.col_values(names_column)):
            if name in it:
                return i + 1
        return -1

    def stop(self):
        self.stopped = True

    def mainloop(self):
        t = 0
        while not self.stopped:
            range_ = rowcol_to_a1(self.person_number,  self.first_task_column) + ':' + rowcol_to_a1(self.person_number, self.worksheet.col_count)
            data = self.worksheet.get(range_)
            self.on_got_marks(data[0])
            time.sleep(1)
            if t % 10 == 0:
                self.load_worksheet()


class DiscraSpectator(Spectator):
    def __init__(self, gc, person_name):
        super().__init__(gc, '1BxCbaE65SVw9sfujC-k9dzSZiQQKXFgBcc17yOXhFW4', person_name, 1, 7)

    def choose_worksheet(self, worksheets):
        sheet_hws = [it for it in worksheets if it.title.startswith('Д') and it.title[1:].isdigit()]
        sheet_hws.sort(key=lambda it: int(it.title[1:]))
        return sheet_hws[-1]

    def on_delta(self, number, was, now):
        match now:
            case 'T':
                notify(f'Зачтена задача {number}')
            case '1':
                notify(f'Отмечена задача {number}')
            case 'P':
                notify(f'Вам выдана задача {number}')
            case '':
                notify(f'Очищено поле в задаче {number}')
            case _:
                notify(f'Невалидное значение в задаче {number}: было `{was}`, теперь `{now}`')


class TestDiscraSpectator(Spectator):
    def __init__(self, gc, person_name):
        super().__init__(gc, '1sTm3pEvPr2Wdvy4toi_rNneQ4bi5nO8aA2sjaCC13Sk', person_name, 1, 7)

    def choose_worksheet(self, worksheets):
        return DiscraSpectator.choose_worksheet(self, worksheets)

    def on_delta(self, number, was, now):
        return DiscraSpectator.on_delta(self, number, was, now)