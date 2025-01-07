def copy_docstring(from_func):
    """Decorator function to assign a docstring from another function."""

    def decorator(to_func):
        to_func.__doc__ = from_func.__doc__

        def wrapper(*args, **kwargs):
            return to_func(*args, **kwargs)

        return wrapper

    return decorator
