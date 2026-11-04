from .abc_notifier import Notifier


class ConsoleNotifier(Notifier):
    def notify(self, text):
        print(f'[NOTIFY] {text}')