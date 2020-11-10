def merge(*args):
    d = {}
    for arg in args:
        d.update(arg)
    return d