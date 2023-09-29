# This file is placed in the Public Domain.
#
# pylint: disable=E0611,E0402,C0301,C0413,C0115,C0116,W0212,R1710,R0903,C0411
# pylint: disable=W0125


"runtime"


import os
import sys
import termios
import time
import traceback
import _thread


from .client  import Client
from .command import Commands, command
from .default import Default
from .error   import Errors, debug
from .parse   import parse
from .store   import Storage, store
from .thread  import launch
from .utils   import mods, pidfile, spl


PIDFILE = store("zelf.pid")
TIME = time.ctime(time.time()).replace("  ", " ")


Cfg = Default()
Cfg.mod = "bsc,err,flt,mod,sts,thr"
Cfg.name = "zelf"
Cfg.slogan = "the self"
Cfg.version = "102"
Cfg.description = f"{Cfg.name.upper()} {Cfg.version} {Cfg.mod.upper()} {Cfg.slogan}"


from . import modules


class CLI(Client):

    output = print

    def raw(self, txt):
        if CLI.output:
            CLI.output(txt)


class Console(CLI):

    def announce(self, txt):
        pass

    def handle(self, evt):
        command(evt)
        evt.wait()

    def prompt(self):
        return input("> ")

    def poll(self):
        return self.event(self.prompt())


def daemon():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    os.umask(0)
    with open('/dev/null', 'r', encoding="utf-8") as sis:
        os.dup2(sis.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as sos:
        os.dup2(sos.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as ses:
        os.dup2(ses.fileno(), sys.stderr.fileno())


def scan(pkg, modnames="", initer=False, dowait=False) -> []:
    if not pkg:
        return []
    inited = []
    scanned = []
    threads = []
    for modname in spl(modnames):
        module = getattr(pkg, modname, None)
        if not module:
            continue
        scanned.append(modname)
        Commands.scan(module)
        Storage.scan(module)
        if initer:
            try:
                module.init
            except AttributeError:
                continue
            inited.append(modname)
            threads.append(launch(module.init, name=f"init {modname}"))
    if dowait:
        for thread in threads:
            thread.join()
    return inited


def wrap(func) -> None:
    if "d" in Cfg.opts:
        debug("terminal disabled!")
        return
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        pass
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
    for exc in Errors.errors:
        traceback.print_exception(
                                  type(exc),
                                  exc,
                                  exc.__traceback__
                                 )


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    if "d" in Cfg.opts:
        daemon()
        pidfile(PIDFILE)
        scan(modules, Cfg.mod, True)
        while 1:
            time.sleep(1.0)
        return
    if "a" in Cfg.opts:
        Cfg.mod = ",".join(mods(modules.__path__[0]))
    if "v" in Cfg.opts:
        Errors.output = print
        Cfg.description = f"{Cfg.name.upper()} {Cfg.version} {Cfg.mod.upper()} {Cfg.opts.upper()}"
        debug(Cfg.description)
    if "c" in Cfg.opts:
        scan(modules, Cfg.mod, True, True)
        csl = Console()
        csl.start()
        csl.forever()
    else:
        scan(modules, Cfg.mod)
        cli = CLI()
        evt = cli.event(Cfg.otxt)
        command(evt)
        evt.wait()


def wrapped():
    wrap(main)


if __name__ == "__main__":
    wrapped()
