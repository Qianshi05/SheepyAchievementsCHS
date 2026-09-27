"""Typed Valve binary KeyValues codec with byte-exact round-trip support.

Item = (type_byte, name, value)
  0x00 -> value is Obj (nested object)
  0x01 -> value is str   (UTF-8 cstring)
  0x02 -> value is int   (int32 LE)
  0x03 -> value is float (float32 LE)
  0x04 -> value is int   (uint32 LE)
  0x07 -> value is int   (uint64 LE)
An object is a list of items and is terminated by a single 0x08 byte.
"""
import struct

END = 0x08
OBJ = 0x00
STR = 0x01
INT32 = 0x02
FLOAT32 = 0x03
UINT32 = 0x04
UINT64 = 0x07


class Obj(list):
    """A KeyValues object: an ordered list of (type, name, value) tuples."""

    def find(self, name):
        for item in self:
            if item[1] == name:
                return item
        return None

    def get(self, name):
        item = self.find(name)
        return None if item is None else item[2]

    def set(self, name, value):
        item = self.find(name)
        if item is None:
            raise KeyError(name)
        item[2] = value

    def keys(self):
        return [i[1] for i in self]


def parse(data, pos=0):
    obj = Obj()
    n = len(data)
    while True:
        if pos >= n:
            raise ValueError("truncated input at offset %d" % pos)
        t = data[pos]
        pos += 1
        if t == END:
            return obj, pos
        end = data.index(b"\x00", pos)
        name = data[pos:end].decode("utf-8", "replace")
        pos = end + 1
        if t == OBJ:
            value, pos = parse(data, pos)
        elif t == STR:
            end = data.index(b"\x00", pos)
            value = data[pos:end].decode("utf-8", "replace")
            pos = end + 1
        elif t == INT32:
            value = struct.unpack_from("<i", data, pos)[0]
            pos += 4
        elif t == FLOAT32:
            value = struct.unpack_from("<f", data, pos)[0]
            pos += 4
        elif t == UINT32:
            value = struct.unpack_from("<I", data, pos)[0]
            pos += 4
        elif t == UINT64:
            value = struct.unpack_from("<Q", data, pos)[0]
            pos += 8
        else:
            raise ValueError("unknown KV type %#x at offset %d" % (t, pos - 1))
        obj.append((t, name, value))


def serialize(obj):
    out = bytearray()
    for t, name, value in obj:
        out.append(t)
        out += name.encode("utf-8") + b"\x00"
        if t == OBJ:
            out += serialize(value)
        elif t == STR:
            out += value.encode("utf-8") + b"\x00"
        elif t == INT32:
            out += struct.pack("<i", value)
        elif t == FLOAT32:
            out += struct.pack("<f", value)
        elif t == UINT32:
            out += struct.pack("<I", value)
        elif t == UINT64:
            out += struct.pack("<Q", value)
        else:
            raise ValueError("unknown KV type %#x" % t)
    out.append(END)
    return bytes(out)


def load(path):
    with open(path, "rb") as fh:
        data = fh.read()
    root, pos = parse(data)
    return root, pos, data


def dumps_tree(obj, indent=0, out=None):
    """Human-readable dump for inspection."""
    out = [] if out is None else out
    pad = "  " * indent
    for t, name, value in obj:
        if t == OBJ:
            out.append("%s%s {" % (pad, name))
            dumps_tree(value, indent + 1, out)
            out.append("%s}" % pad)
        else:
            out.append("%s%s = %r" % (pad, name, value))
    return out
