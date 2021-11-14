from functools import wraps


def disable_for_loaddata(signal_handler):
    """
    Decorator that turns off signal handlers when loading fixture data.
    """

    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        try:
            if kwargs["raw"]:
                return
        except KeyError:
            pass
        signal_handler(*args, **kwargs)

    return wrapper
