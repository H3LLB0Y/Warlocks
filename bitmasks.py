# bitmasks

from panda3d.core import BitMask32

NOTARENA=BitMask32.allOn()
NOTARENA.setBitTo(31,False)
ARENAMASK=BitMask32.bit(31)
