# This file is placed in the Public Domain.
#
# pylint: disable=C0112,C0115,C0116,W0105,R0903,E0402,C0209,R1710


"persistence"


import inspect
import os


from .method import fqn, ident, search
from .object import Object, keys, read, update, write
from .utils  import cdir, fntime, strip


class Storage:

    classes = {}
    workdir = os.path.expanduser('~/.%s' % __file__.split(os.sep)[-2])

    @staticmethod
    def add(clz):
        if not clz:
            return
        name = str(clz).split()[1][1:-2]
        Storage.classes[name] = clz

    @staticmethod
    def scan(mod) -> None:
        for key, clz in inspect.getmembers(mod, inspect.isclass):
            if key.startswith("cb"):
                continue
            if not issubclass(clz, Object):
                continue
            Storage.add(clz)


def find(mtc, selector=None) -> []:
    if selector is None:
        selector = {}
    for fnm in reversed(sorted(fns(mtc), key=fntime)):
        obj = Object()
        fetch(obj, fnm)
        if '__deleted__' in obj:
            continue
        if selector and not search(obj, selector):
            continue
        yield obj


def fns(mtc) -> []:
    dname = ''
    clz = long(mtc)
    pth = None
    if clz:
        pth = store(clz)
    if not pth:
        return []
    for rootdir, dirs, _files in os.walk(pth, topdown=False):
        if dirs:
            dname = sorted(dirs)[-1]
            if dname.count('-') == 2:
                ddd = os.path.join(rootdir, dname)
                fls = sorted(os.listdir(ddd))
                if fls:
                    yield strip(os.path.join(ddd, fls[-1]))


def long(name):
    split = name.split(".")[-1].lower()
    res = None
    for named in keys(Storage.classes):
        if split in named.split(".")[-1].lower():
            res = named
            break
    return res


def path(pth):
    pth =  os.path.join(Storage.workdir, pth)
    cdir(pth)

def store(pth=""):
    pth = os.path.join(Storage.workdir, "store", pth)
    cdir(pth)
    return pth


"methods"


def fetch(obj, pth):
    pth2 = store(pth)
    read(obj, pth2)
    obj.__fnm__ = strip(pth)


def last(obj, selector=None) -> None:
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x.__fnm__)
                   )
    if result:
        inp = result[-1]
        update(obj, inp)
        obj.__fnm__ = inp.__fnm__


def sync(obj, pth=None):
    pth = pth or obj.__fnm__
    if not pth:
        pth = ident(obj)
    pth2 = store(pth)
    write(obj, pth2)
    obj.__fnm__ = pth
