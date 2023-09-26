# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,W0212,E0402,W0201,W0613,E1120,R0902,W0105,W0612
# pylint: disable=W0718,C0103


"messaging"


from .broker  import byorig
from .default import Default


def __dir__():
    return (
            'Event',
           )


__all__ = __dir__()


class Event(Default):

    def ready(self) -> None:
        if "_ready" in self:
            self._ready.set()

    def reply(self, txt) -> None:
        if "result" in self:
            self.result.append(txt)

    def show(self):
        if "channel" not in self:
            channel = ""
        else:
            channel = self.channel
        bot = byorig(self.orig)
        if bot:
            for txt in self.result:
                bot.say(channel, txt)

    def wait(self) -> []:
        if "_thr" in self:
            self._thr.join()
        if "_ready" in self:
            self._ready.wait()
        if "_result" in self:
            return self._result
        return []
