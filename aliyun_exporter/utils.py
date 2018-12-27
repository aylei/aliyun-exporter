def format_metric(text: str):
    return text.replace('.', '_')


def format_period(text: str):
    return text.split(',', 1)[0]
