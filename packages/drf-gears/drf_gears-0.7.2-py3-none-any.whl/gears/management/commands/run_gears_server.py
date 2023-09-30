import importlib

from django.core.management.commands.runserver import Command as RunServerOriginal

from gears.settings import get_settings


def str2obj(reference: str):
    module_name, func = reference.rsplit(".", maxsplit=1)
    module = importlib.import_module(module_name)
    return getattr(module, func)


def obj2str(obj):
    return f"{obj.__module__}.{obj.__class__.__name__}"


class Command(RunServerOriginal):
    def __init__(self):
        self.settings = get_settings()

    def handle(self, *args, **options):
        self.run_tasks()
        super().handle(*args, **options)

    def run_tasks(self):
        for task in self.get_tasks('up'):
            task()
        try:
            while True:
                pass
        except (KeyboardInterrupt, SystemExit):
            for task in self.get_tasks('down'):
                task()

    def get_tasks(self, t: str):
        return [str2obj(task) for task in self.settings[f'run_gears_server_{t}_tasks']]
