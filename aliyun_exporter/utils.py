def format_metric(text: str):
    return text.replace('.', '_')


def format_period(text: str):
    return text.split(',', 1)[0]


def try_or_else(op, default):
    try:
        return op()
    except:
        return default

