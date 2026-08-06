#!/usr/bin/env python3

_license = """
big
Copyright 2022-2026 Larry Hastings
All rights reserved.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
The source of truth for big.stylesheet's stock ANSI color palettes.

The 26-color vocabulary (red/orange/yellow/green/cyan/blue/purple/gray,
each in light/dark/normal, plus white/black) plus the four attributes,
rendered at four color depths:

    ansi_truecolor   24-bit (the master values)
    ansi_256         xterm-256, nearest-matched from the 24-bit values
    ansi_16          the 16-color SGR codes, an explicit hand-mapping
    ansi_uncolored   the attributes only, color dropped

big/stylesheet.py carries these HARD-CODED, so nothing is computed at
import.  This file generates that hard-coded block.  Run it and paste
its output over the generated block in big/stylesheet.py:

    python3 resources/stylesheet/palettes.py

The output carries a sha256 of this file, so you can tell whether the
pasted block is stale (its hash won't match this file's).
"""

import datetime
import hashlib


_ansi_attributes = {
    'bold':          ('T', '\x1b[1mT\x1b[22m'),
    'italic':        ('T', '\x1b[3mT\x1b[23m'),
    'underline':     ('T', '\x1b[4mT\x1b[24m'),
    'strikethrough': ('T', '\x1b[9mT\x1b[29m'),
}

# each hue: (dark, normal, light) as six hex digits
_palette_rgb = {
    'red':    ('850000', 'BA0000', 'E00000'),
    'orange': ('AD3E00', 'C74800', 'FF5C00'),
    'yellow': ('A89000', 'E3C000', 'F5DE00'),
    'green':  ('1E7A3C', '2FA65A', '5FD088'),
    'cyan':   ('0E6B78', '1AA0B0', '4FCEDC'),
    'blue':   ('0E2E88', '2F72C0', '6BA6E6'),
    'purple': ('63108A', '9040B8', 'B87AD8'),
    'gray':   ('4D4D4D', '808080', 'B3B3B3'),
}
_palette_white, _palette_black = 'FFFFFF', '000000'

# each hue: (dark, normal, light) SGR foreground code
_palette_16 = {
    'red':    (31, 31, 91),
    'orange': (91, 91, 93),
    'yellow': (33, 33, 93),
    'green':  (32, 32, 92),
    'cyan':   (36, 36, 96),
    'blue':   (34, 34, 94),
    'purple': (35, 35, 95),
    'gray':   (90, 90, 37),
}
_palette_16_white, _palette_16_black = 97, 30

_ansi_cube = (0, 95, 135, 175, 215, 255)


def _hex_rgb(h):
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _nearest_256(r, g, b):
    "The xterm-256 index nearest (r,g,b): the 6x6x6 cube or the gray ramp."
    def level(v):
        return min(range(6), key=lambda i: abs(_ansi_cube[i] - v))
    lr, lg, lb = level(r), level(g), level(b)
    cube = 16 + 36 * lr + 6 * lg + lb
    cr, cg, cb = _ansi_cube[lr], _ansi_cube[lg], _ansi_cube[lb]
    cube_d = (cr - r) ** 2 + (cg - g) ** 2 + (cb - b) ** 2
    gi = min(range(24), key=lambda i: abs((8 + 10 * i) - (r + g + b) / 3))
    gv = 8 + 10 * gi
    gray_d = (gv - r) ** 2 + (gv - g) ** 2 + (gv - b) ** 2
    return cube if cube_d <= gray_d else 232 + gi


def _rgb_vocab():
    "Yield (name, hex) for all 26 colors."
    for hue, (dark, normal, light) in _palette_rgb.items():
        yield hue, normal
        yield 'light_' + hue, light
        yield 'dark_' + hue, dark
    yield 'white', _palette_white
    yield 'black', _palette_black


def _code16_vocab():
    "Yield (name, SGR code) for all 26 colors."
    for hue, (dark, normal, light) in _palette_16.items():
        yield hue, normal
        yield 'light_' + hue, light
        yield 'dark_' + hue, dark
    yield 'white', _palette_16_white
    yield 'black', _palette_16_black


def _fg24(h):
    r, g, b = _hex_rgb(h)
    return ('T', f'\x1b[38;2;{r};{g};{b}mT\x1b[39m')

def _fg256(h):
    return ('T', f'\x1b[38;5;{_nearest_256(*_hex_rgb(h))}mT\x1b[39m')

def _fg16(code):
    return ('T', f'\x1b[{code}mT\x1b[39m')


def _entries(color, vocab):
    "The attributes, then every color rendered by `color`."
    entries = list(_ansi_attributes.items())
    entries += [(name, color(value)) for name, value in vocab()]
    return entries


def _emit(name, entries):
    lines = [f'{name} = StyleSheet({{']
    for key, value in entries:
        lines.append(f'    {key!r}: {value!r},')
    lines.append('})')
    lines.append(f"export({name!r})")
    return '\n'.join(lines)


def main():
    with open(__file__, 'rb') as f:
        digest = hashlib.sha256(f.read()).hexdigest()
    now = datetime.datetime.now().isoformat(timespec='seconds')

    print(f"# Generated by resources/stylesheet/palettes.py")
    print(f"# at {now}; sha256(palettes.py) = {digest}")
    print(f"# Do not hand-edit -- edit palettes.py and regenerate.")
    print()
    print(_emit('ansi_truecolor', _entries(_fg24, _rgb_vocab)))
    print()
    print(_emit('ansi_256', _entries(_fg256, _rgb_vocab)))
    print()
    print(_emit('ansi_16', _entries(_fg16, _code16_vocab)))
    print()
    print(_emit('ansi_uncolored', _entries(lambda value: ('T', 'T'), _rgb_vocab)))


if __name__ == "__main__":
    main()
