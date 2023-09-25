''' Utility routines.'''
import sys
from io import StringIO
import logging


class Capturing(list):
    # Capture stdout print() statements into object for logging
    #
    # Usage: (use `with` context modifier)
    #     with Capturing(<prev_lines>) as output:
    #         do_something(my_object)
    #     print(output)
    #
    # Args:
    #   previous_lines (optional List(str))
    def __enter__(self):
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout

    def __str__(self):
        return '\n'.join(self)

class ToLogLevel(dict):
    def __init__(self):
        self.int_data = {
            0: logging.FATAL,
            1: logging.ERROR,
            2: logging.WARNING,
            3: logging.DEBUG,
            4: logging.INFO}
        self.str_data = dict(
            FATAL=logging.FATAL,
            CRITICAL=logging.CRITICAL,
            ERROR=logging.ERROR,
            WARNING=logging.WARNING,
            DEBUG=logging.DEBUG,
            INFO=logging.INFO
        )
        self.int_max = 4

    def __getitem__(self, key):
        '''translate the numeric string or 0-3 debug level to the logging level'''
        assert (isinstance(key,int) and key >= 0) or (key in self.str_data), f'level key: "{key}" not found'
        
        if isinstance(key,int):
            if key > self.int_max:
                key = self.int_max
            return self.int_data[key]
        elif isinstance(key,str):
            return self.str_data[key]
        else:
            return key
        
    def __setitem__(self, __key, __value) -> None:
        raise NotImplementedError('cannot set values on this object')

log_level_dict = ToLogLevel()
