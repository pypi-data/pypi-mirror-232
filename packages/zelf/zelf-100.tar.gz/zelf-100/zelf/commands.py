# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,E0402,W0201,W0613,E1120,R0902,W0105,W0612
# pylint: disable=W0718,W4901


"command"


import inspect


from .errors import Errors
from .object import Object
from .parser import parse


def __dir__():
    return (
            'Commands',
            'command'
           )


__all__ = __dir__()


class Commands:

    cmds = Object()

    @staticmethod
    def add(func):
        Commands.cmds[func.__name__] = func

    @staticmethod
    def scan(mod) -> None:
        for key, cmd in inspect.getmembers(mod, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in cmd.__code__.co_varnames:
                Commands.add(cmd)


def command(evt):
    parse(evt, evt.txt)
    evt.type = "command"
    func = getattr(Commands.cmds, evt.cmd, None)
    if func:
        try:
            func(evt)
            evt.show()
        except Exception as ex:
            exc = ex.with_traceback(ex.__traceback__)
            Errors.errors.append(exc)
    evt.ready()
