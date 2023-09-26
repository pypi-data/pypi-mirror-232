# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,E0402


"output"


import queue
import textwrap
import threading


from .broker import byorig
from .cache  import Cache
from .censor import doskip


class TextWrap(textwrap.TextWrapper):

    def __init__(self):
        super().__init__()
        self.break_long_words = False
        self.drop_whitespace = True
        self.fix_sentence_endings = True
        self.replace_whitespace = True
        self.tabsize = 4
        self.width = 450


wrapper = TextWrap()


class Output(Cache):

    def __init__(self):
        Cache.__init__(self)
        self.dostop = threading.Event()
        self.oqueue = queue.Queue()

    def dosay(self, channel, txt):
        raise NotImplementedError

    def gettxt(self, channel):
        txt = None
        try:
            che = self.cache.get(channel, None)
            if che:
                txt = che.pop(0)
        except (KeyError, IndexError):
            pass
        return txt

    def oput(self, channel, txt):
        if channel is None or txt is None:
            return
        if channel not in self.cache:
            self.cache[channel] = []
        self.oqueue.put_nowait((channel, txt))

    def out(self):
        while not self.dostop.is_set():
            (channel, txt) = self.oqueue.get()
            if doskip(txt):
                continue
            if channel is None and txt is None:
                break
            if self.dostop.is_set():
                break
            try:
                txtlist = wrapper.wrap(txt)
            except AttributeError:
                continue
            if len(txtlist) > 3:
                Output.extend(channel, txtlist)
                length = len(txtlist)
                self.dosay(
                             channel,
                             f"use !mre to show more (+{length})"
                            )
                continue
            _nr = -1
            for txt in txtlist:
                _nr += 1
                self.dosay(channel, txt)

    def size(self, channel):
        return len(self.cache[channel])


def mre(event):
    if not event.channel:
        event.reply('channel is not set.')
        return
    bot = byorig(event.orig)
    if 'cache' not in dir(bot):
        event.reply('bot is missing cache')
        return
    if event.channel not in bot.cache:
        event.reply(f'no output in {event.channel} cache.')
        return
    for _x in range(3):
        txt = bot.gettxt(event.channel)
        if txt:
            bot.say(event.channel, txt)
    size = bot.size(event.channel)
    event.reply(f'{size} more in cache')
