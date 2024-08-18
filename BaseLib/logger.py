import builtins
import datetime
import inspect


original_print = builtins.print


_split_str = "Budget_Buckets/"
class Logger:
    caller: str
    "Where the logging is happening, prefixed to each line"
    
    def __init__(self, caller: str) -> None:
        self.caller = caller
    
    def prefix(self):
        """Assembles the line prefix"""
        now = datetime.datetime.now().strftime("%H:%M:%S.%f")
        return f"{now} - {self.caller}:"

    def print(self, *values, **kwargs):
        original_print(self.prefix(), *values, **kwargs)


_delegate_dict: dict[str, Logger] = {}
def delegate_print(*values, **kwargs):
    """Delegates `print` to the Logger class"""
    caller = inspect.stack()[1].filename
    caller = caller.split(_split_str)[-1]
    if caller not in _delegate_dict:
        _delegate_dict[caller] = Logger(caller=caller)
    logger = _delegate_dict[caller]
    logger.print(*values, **kwargs)
