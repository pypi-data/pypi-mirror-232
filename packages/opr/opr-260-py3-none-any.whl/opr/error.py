# This file is placed in the Public Domain.
#
# pylint: disable=C0115,C0103,C0116,E1102,R0903


"exceptions"


class Errors:

    errors = []
    output = None
    skip = ["PING", "PONG", 'PRIVMSG']


def debug(txt):
    if not Errors.output:
        return
    donext = False
    for skp in Errors.skip:
        if skp in txt:
            donext = True
    if donext:
        return
    Errors.output(txt)
