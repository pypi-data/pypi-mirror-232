# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,E0402,W0201,W0613,E1120,R0902,W0105,W0612
# pylint: disable=W0718


"client"


import time
import _thread


from .broker  import Broker
from .command import command
from .event   import Event
from .reactor import Reactor


def __dir__():
    return (
            'Client',
           )


class Client(Reactor):

    def __init__(self):
        Reactor.__init__(self)
        self.register("command", command)
        Broker.add(self)

    def announce(self, txt):
        self.raw(txt)

    def event(self, txt):
        evt = Event()
        evt.txt = txt
        evt.orig = object.__repr__(self)
        evt.type = "command"
        return evt

    def forever(self):
        while 1:
            try:
                time.sleep(1.0)
            except (EOFError, KeyboardInterrupt):
                _thread.interrupt_main()

    def raw(self, txt):
        pass

    def say(self, channel, txt):
        self.raw(txt)
