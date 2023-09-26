# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0116,R0912,R0915,W0105,E0402,R0903


"users"


import time


from .default import Default
from .storage import find, sync
from .utils   import fntime, laps


class NoUser(Exception):

    pass


class User(Default):

    def __init__(self):
        Default.__init__(self)
        self.user = ''
        self.perms = []


class Users:

    @staticmethod
    def allowed(origin, perm):
        perm = perm.upper()
        user = Users.get_user(origin)
        val = False
        if user and perm in user.perms:
            val = True
        return val

    @staticmethod
    def delete(origin, perm):
        res = False
        for user in Users.get_users(origin):
            try:
                user.perms.remove(perm)
                sync(user)
                res = True
            except ValueError:
                pass
        return res

    @staticmethod
    def get_users(origin=''):
        selector = {'user': origin}
        return find('user', selector)

    @staticmethod
    def get_user(origin):
        users = list(Users.get_users(origin))
        res = None
        if users:
            res = users[-1]
        return res

    @staticmethod
    def perm(origin, permission):
        user = Users.get_user(origin)
        if not user:
            raise NoUser(origin)
        if permission.upper() not in user.perms:
            user.perms.append(permission.upper())
            sync(user)
        return user


def dlt(event):
    if not event.args:
        event.reply('dlt <username>')
        return
    selector = {'user': event.args[0]}
    nrs = 0
    for obj in find('user', selector):
        nrs += 1
        obj.__deleted__ = True
        sync(obj)
        event.reply('ok')
        break
    if not nrs:
        event.reply( "no users")


def met(event):
    if not event.args:
        nmr = 0
        for obj in find('user'):
            lap = laps(time.time() - fntime(obj.__fnm__))
            event.reply(f'{nmr} {obj.user} {obj.perms} {lap}s')
            nmr += 1
        if not nmr:
            event.reply('no user')
        return
    user = User()
    user.user = event.rest
    user.perms = ['USER']
    sync(user)
    event.reply('ok')
