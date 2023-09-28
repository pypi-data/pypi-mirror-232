import colorama

from .bb_parser import *
from .legacy import *
from .style import *

colorama.init()

__all__ = [
    "print",
    "print_chapter",
    "warning",
    "error",
    "fatal",
    "input",
    "ask",
    "ask_short",
    "ask_yes_no",
]
