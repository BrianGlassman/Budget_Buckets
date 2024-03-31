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