import requests

from .abc_notifier import Notifier


def tg_notify(text, id_):
    requests.get(
        'https://dprofe.ddns.net/tg-notify',
        {
            'message': text,
            'id': id_,
        }
    )


class TgNotifier(Notifier):
    def __init__(self, tg_id):
        self.tg_id = tg_id

    def notify(self, text):
        tg_notify(f'[Table fetcher] {text}', self.tg_id)