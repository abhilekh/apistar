"""
My decorator methods to make the code easier.
Please put all your decorator utils here.
"""

import functools


def auto_str(cls):
    """
       Auto generate string for class.
    """
    def __str__(self):
        return '%s(%s)' % (
            type(self).__name__,
            ', '.join('%s=%s' % (k, str(v) if not isinstance(v, (list, tuple))
                                 else "[{0}]".format(", ".join([str(item) for item in v])))
                      for (k, v) in vars(self).items())
        )
    cls.__str__ = __str__
    return cls


def rename_kwargs(**replacements):
    """
    Renaming the argument. Useful in argparse/click.
    """
    def actual_decorator(func):
        @functools.wraps(func)
        def decorated_func(*args, **kwargs):
            for internal_arg, external_arg in replacements.items():
                if external_arg in kwargs:
                    kwargs[internal_arg] = kwargs.pop(external_arg)
            return func(*args, **kwargs)
        return decorated_func
    return actual_decorator


if __name__ == "__main__":
    # This will not raise cyclic import
    import apistar.document as mdoc
    auto_str(mdoc.Document)
