"""
rencode -- Web safe object pickling/unpickling.

Public domain, Connelly Barnes 2006-2007.

The rencode module is a modified version of bencode from the
BitTorrent project.  For complex, heterogeneous data structures with
many small elements, r-encodings take up significantly less space than
b-encodings:

 >>> len(rencode.dumps({'a':0, 'b':[1,2], 'c':99}))
 13
 >>> len(bencode.bencode({'a':0, 'b':[1,2], 'c':99}))
 26

The rencode format is not standardized, and may change with different
rencode module versions, so you should check that you are using the
same rencode version throughout your project.
"""

# Original bencode module by Petru Paler, et al.
#
# Modifications by Connelly Barnes:
#
#  - Added support for floats (sent as 32-bit or 64-bit in network
#    order), bools, None.
#  - Allowed dict keys to be of any serializable type.
#  - Lists/tuples are always decoded as tuples (thus, tuples can be
#    used as dict keys).
#  - Embedded extra information in the 'typecodes' to save some space.
#  - Added a restriction on integer length, so that malicious hosts
#    cannot pass us large integers which take a long time to decode.
#
# Licensed by Bram Cohen under the "MIT license":
#
#  "Copyright (C) 2001-2002 Bram Cohen
#
#  Permission is hereby granted, free of charge, to any person
#  obtaining a copy of this software and associated documentation files
#  (the "Software"), to deal in the Software without restriction,
#  including without limitation the rights to use, copy, modify, merge,
#  publish, distribute, sublicense, and/or sell copies of the Software,
#  and to permit persons to whom the Software is furnished to do so,
#  subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be
#  included in all copies or substantial portions of the Software.
#
#  The Software is provided "AS IS", without warranty of any kind,
#  express or implied, including but not limited to the warranties of
#  merchantability,  fitness for a particular purpose and
#  noninfringement. In no event shall the  authors or copyright holders
#  be liable for any claim, damages or other liability, whether in an
#  action of contract, tort or otherwise, arising from, out of or in
#  connection with the Software or the use or other dealings in the
#  Software."
#
# (The rencode module is licensed under the above license as well).
#

from types import (
    IntType, TupleType, StringType,
    FloatType, LongType, ListType,
    DictType, NoneType, BooleanType, UnicodeType
)

from struct import pack, unpack
from cStringIO import StringIO
import zlib

class EncodeError(Exception): pass
class DecodeError(Exception): pass

HEADER = "SRW3"

protocol = {
    TupleType  :"T",
    ListType   :"L",
    DictType   :"D",
    LongType   :"B",
    IntType    :"I",
    FloatType  :"F",
    StringType :"S",
    NoneType   :"N",
    BooleanType:"b",
    UnicodeType:"U"
}

encoder = {}
class register_encoder_for_type(object):
    """Registers an encoder function, for a type, in the global encoder dictionary."""
    def __init__(self, t):
        self.type = t
    def __call__(self, func):
        encoder[self.type] = func
        return func

#contains dictionary of decoding functions, where the dictionary key is the type prefix used.
decoder = {}
class register_decoder_for_type(object):
    """Registers a decoder function, for a prefix, in the global decoder dictionary."""
    def __init__(self, t):
        self.prefix = protocol[t]
    def __call__(self, func):
        decoder[self.prefix] = func
        return func

## <encoding functions> ##
@register_encoder_for_type(DictType)
def enc_dict_type(obj):
    data = "".join([encoder[type(i)](i) for i in obj.items()])
    return "%s%s%s" % ("D", pack("!L", len(data)), data)

@register_encoder_for_type(TupleType)
@register_encoder_for_type(ListType)
def enc_list_type(obj):
    data = "".join([encoder[type(i)](i) for i in obj])
    return "%s%s%s" % (protocol[type(obj)], pack("!L", len(data)), data)

@register_encoder_for_type(IntType)
def enc_int_type(obj):
    return "%s%s" % (protocol[IntType], pack("!i", obj))

@register_encoder_for_type(FloatType)
def enc_float_type(obj):
    return "%s%s" % (protocol[FloatType], pack("!d", obj))

@register_encoder_for_type(LongType)
def enc_long_type(obj):
    obj = hex(obj)[2:-1]
    return "%s%s%s" % (protocol[LongType], pack("!L", len(obj)), obj)

@register_encoder_for_type(UnicodeType)
def enc_unicode_type(obj):
    obj = obj.encode('utf-8')
    return "%s%s%s" % (protocol[UnicodeType], pack("!L", len(obj)), obj)


@register_encoder_for_type(StringType)
def enc_string_type(obj):
    return "%s%s%s" % (protocol[StringType], pack("!L", len(obj)), obj)

@register_encoder_for_type(NoneType)
def enc_none_type(obj):
    return protocol[NoneType]

@register_encoder_for_type(BooleanType)
def enc_bool_type(obj):
    return protocol[BooleanType] + str(int(obj))

def dumps(obj, compress=False):
    """Encode simple Python types into a binary string."""
    option = "N"
    if compress: option = "Z"
    try:
        data = encoder[type(obj)](obj)
        if compress: data = zlib.compress(data)
        return "%s%s%s" % (HEADER, option, data)
    except KeyError, e:
        raise EncodeError, "Type not supported. (%s)" % e
## </encoding functions> ##

## <decoding functions> ##
def build_sequence(data, cast=list):
    size = unpack('!L', data.read(4))[0]
    items = []
    data_tell = data.tell
    data_read = data.read
    items_append = items.append
    start_position = data.tell()
    while (data_tell() - start_position) < size:
        T = data_read(1)
        value = decoder[T](data)
        items_append(value)
    return cast(items)

@register_decoder_for_type(TupleType)
def dec_tuple_type(data):
    return build_sequence(data, cast=tuple)

@register_decoder_for_type(ListType)
def dec_list_type(data):
    return build_sequence(data, cast=list)

@register_decoder_for_type(DictType)
def dec_dict_type(data):
    return build_sequence(data, cast=dict)

@register_decoder_for_type(LongType)
def dec_long_type(data):
    size = unpack('!L', data.read(4))[0]
    value = long(data.read(size),16)
    return value

@register_decoder_for_type(StringType)
def dec_string_type(data):
    size = unpack('!L', data.read(4))[0]
    value = str(data.read(size))
    return value

@register_decoder_for_type(FloatType)
def dec_float_type(data):
    value = unpack('!d', data.read(8))[0]
    return value

@register_decoder_for_type(IntType)
def dec_int_type(data):
    value = unpack('!i', data.read(4))[0]
    return value

@register_decoder_for_type(NoneType)
def dec_none_type(data):
    return None

@register_decoder_for_type(BooleanType)
def dec_bool_type(data):
    value = int(data.read(1))
    return bool(value)

@register_decoder_for_type(UnicodeType)
def dec_unicode_type(data):
    size = unpack('!L', data.read(4))[0]
    value = data.read(size).decode('utf-8')
    return value

def loads(data):
    """
    Decode a binary string into the original Python types.
    """
    buffer = StringIO(data)
    header = buffer.read(len(HEADER))
    assert header == HEADER
    option = buffer.read(1)
    decompress = False
    if option == "Z":
        buffer = StringIO(zlib.decompress(buffer.read()))
    try:
        value = decoder[buffer.read(1)](buffer)
    except KeyError, e:
        raise DecodeError, "Type prefix not supported. (%s)" % e

    return value
## </decoding functions> ##

try:
    import psyco
    dumps = psyco.proxy(dumps)
    loads = psyco.proxy(loads)
except ImportError:
    pass

if __name__ == "__main__":
    value = (u'\N{POUND SIGN} Testing unicode', {True:False},[1,2,3,4],["simon"],("python is","cool"),
"pi equals",3.14,("longs are ok",
912398102398102938102398109238019283012983019238019283019283))
    data = dumps(value)
    print data
    x = loads(data)
    print x