import os

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")


def fixture(filename):
    return open(path(filename), "rb")


def path(filename):
    return os.path.join(FIXTURES, filename)
