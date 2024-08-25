# General imports
import datetime as _datetime
import json as _json

# Project imports
from .money import MoneyEncoder, MoneyDecoder


def safe_open(*args, **kwargs):
    """Wrapper for "open" to set newline and encoding so that it plays nice"""
    kwargs.setdefault('newline', '')
    kwargs.setdefault('encoding', 'utf8')
    return open(*args, **kwargs)


def json_dump(outfile: str, contents, indent: int|None = None):
    """Sugar syntax for JSON dump using safe_open and MoneyEncoder"""
    with safe_open(outfile, 'w') as f:
        _json.dump(contents, f, indent=indent, cls=MoneyEncoder)


def json_load(infile: str):
    """Sugar syntax for JSON load using safe_open and MoneyDecoder"""
    with safe_open(infile, 'r') as f:
        ret = _json.load(f, cls=MoneyDecoder)
    return ret


def parse_date(date_str) -> _datetime.date:
    return _datetime.datetime.strptime(date_str, '%m/%d/%Y').date()

def unparse_date(date: _datetime.date) -> str:
    # Can't just use strftime because it includes leading zeroes
    # Can remove leading zeroes using "-" (Unix) or "#" (Windows), but this way is more portable
    return f'{date.month}/{date.day}/{date.year}'

def format_cell_value(value) -> str:
    """Convert an openpyxl Cell value to a string the same as in a CSV"""
    if value is None:
        return ''
    elif isinstance(value, _datetime.datetime):
        return unparse_date(value)
    else:
        return str(value)
