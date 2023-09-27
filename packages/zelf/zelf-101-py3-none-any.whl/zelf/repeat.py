# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,E0402,W0105,W0718,R0903


"repeater"


from .timer  import Timer
from .thread import launch


def __dir__():
    return (
            'Repeater',
           )


class Repeater(Timer):

    def run(self):
        thr = launch(self.start)
        super().run()
        return thr
