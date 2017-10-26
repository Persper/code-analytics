import os


def get_parent_dir(path):
    return os.path.abspath(os.path.join(path, os.pardir))


root_path = get_parent_dir(
    get_parent_dir(os.path.dirname(os.path.abspath(__file__))))
