import os

from time import sleep
import random
import subprocess
from dataclasses import dataclass, is_dataclass


def create_dir_if_not_exists(path):
    os.makedirs(path, exist_ok=True)


def check_path_exists(path):
    return os.path.exists(path)


def setup_dir_for_file_path(file_path: str):
    create_dir_if_not_exists("/".join(file_path.split("/")[:-1]))


def random_sleep(f: int, t: int):
    rand_num = random.uniform(f, t)
    rand_num = format(rand_num, ".3f")
    rand_num = float(rand_num)
    sleep(rand_num)


def cleanup_string(s: str):
    return s.replace(" ", "").replace("\t", "").replace("\n", "")


def get_abspath(relative_path: str):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), f"../{relative_path}")
    )


def send_mac_native_notification(message):
    title = "Python Notification"
    subtitle = "Python Notification"
    applescript_command = (
        'display notification "{}" with title "{}" subtitle "{}"'.format(
            message, title, subtitle
        )
    )
    subprocess.run(["osascript", "-e", applescript_command])


# https://stackoverflow.com/questions/51564841/creating-nested-dataclass-objects-in-python


def nested_dataclass(*args, **kwargs):
    def wrapper(cls):
        cls = dataclass(cls, **kwargs)
        original_init = cls.__init__

        def __init__(self, *args, **kwargs):
            for name, value in kwargs.items():
                field_type = cls.__annotations__.get(name, None)
                if is_dataclass(field_type) and isinstance(value, dict):
                    new_obj = field_type(**value)
                    kwargs[name] = new_obj
            original_init(self, *args, **kwargs)

        cls.__init__ = __init__
        return cls

    return wrapper(args[0]) if args else wrapper
