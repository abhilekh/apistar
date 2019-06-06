import typesystem


def lookup(value: dict, keys: [list, tuple], default: typesystem.Any = None):
    '''Check in my nested dict.'''
    assert isinstance(keys, (list, tuple))
    for key in keys:
        try:
            value = value[key]
        except (KeyError, IndexError, TypeError):
            return default
    return value