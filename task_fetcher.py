import threading
import tkinter as tk

import pyperclip
import requests
from bs4 import BeautifulSoup


class TaskFetcher:
    def __init__(self, url):
        self.soup: BeautifulSoup = None
        self.url = url
        self.tk = tk.Tk()
        self.tk.protocol("WM_DELETE_WINDOW", self.tk.withdraw)

        self.tk.withdraw()
        self.tk.deiconify()
        self.tk.withdraw()


        self.area = tk.Text(self.tk)
        self.area.pack()

        threading.Thread(target=self.fetch).start()

    def fetch(self):
        try:
            self.soup = BeautifulSoup(requests.get(self.url).text, 'lxml')
        except Exception as e:
            print(f'{type(e)}: {e}')
            print('Not loaded((')
        else:
            print('fetched successfully')

    def get_task_from_text(self, number):
        return ''

    def get_task_from_ol(self, number):
        ol = max(self.soup.find_all('ol'), key=len)
        return ol.find_all('li')[number - 1].text

    def show_task(self, number, from_ol=True):
        print(f'Copying task: {number}')
        text = self.get_task_from_ol(number)
        pyperclip.copy(text)

        self.area.delete("1.0", tk.END)
        self.area.insert("1.0", text)

        self.tk.deiconify()

