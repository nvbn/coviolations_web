import os


def get_content(file_name):
    """Get content of near file"""
    return open(os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'fixtures', file_name),
    )).read()
