import os.path


def normpath(path):
    return os.path.normpath(path).replace("\\", "/")


def buildpath(*args):
    return normpath(os.path.join(*args))
