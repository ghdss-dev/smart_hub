import os

def get_full_path(relative_path):

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, relative_path)

def format_detalhes(detalhes):

    formatter_str = ""
    for key, value in detalhes.items():

        formatter_str += f"{key.capitalize()}: {value}\n"

    return formatter_str