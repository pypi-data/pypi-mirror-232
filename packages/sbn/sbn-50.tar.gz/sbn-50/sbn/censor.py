# This file is placed in the Public Domain.
#
# pylint: disable=E0402,C0115,C0116.R0903


"reinforcement degrades performance"


from .object import Object
from .utils  import skip


class Censor(Object):

    skip = []


def doskip(txt):
    return skip(txt, Censor.skip)
