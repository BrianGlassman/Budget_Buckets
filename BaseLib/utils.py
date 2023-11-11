def safe_open(*args, **kwargs):
    """Wrapper for "open" to set newline and encoding so that it plays nice"""
    kwargs.setdefault('newline', '')
    kwargs.setdefault('encoding', 'utf8')
    return open(*args, **kwargs)