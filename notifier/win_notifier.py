from winotify import Notification

from .abc_notifier import Notifier


def win_notify(text):
    Notification(
        'Table notificator',
        'Изменение в таблице!',
        text,
        'C:\\Users\\dima\\PycharmProjects\\table-change-notification\\spreadsheets.ico'
    ).show()
    print(f'Notify: {text}')


class WinNotifier(Notifier):
    def notify(self, text):
        win_notify(text)