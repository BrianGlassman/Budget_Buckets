import datetime


def safe_open(*args, **kwargs):
    """Wrapper for "open" to set newline and encoding so that it plays nice"""
    kwargs.setdefault('newline', '')
    kwargs.setdefault('encoding', 'utf8')
    return open(*args, **kwargs)


def money_equal(v1, v2):
    """Compare two money values"""
    return round(v1, 2) == round(v2, 2)


def format_money(val: str) -> str:
    """Copy Excel's money formatting"""
    return "${:,.2f}".format(float(val)).replace('$-', '-$')


def parse_date(date_str) -> datetime.date:
    return datetime.datetime.strptime(date_str, '%m/%d/%Y').date()

def unparse_date(date: datetime.date) -> str:
    # Can't just use strftime because it includes leading zeroes
    # Can remove leading zeroes using "-" (Unix) or "#" (Windows), but this way is more portable
    return f'{date.month}/{date.day}/{date.year}'