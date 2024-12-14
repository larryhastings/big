# -*- coding: utf-8 -*-

# This file serves a dual purpose in the test suite!
# It both uses an ASCII "source code encoding" line,
# which lets us test decoding those lines.
#
# Also, when run it generates two more Python scripts,
# using unfamiliar encodings, both with BOMs:
#     * "gb18030_bom.py" uses the "gb18030" encoding.
#       This is an encoding defined by the PRC.
#     * "utf-1_bom.py" uses the "UTF-1" encoding,
#       an obsolete encoding replaced by the far
#       superior UTF-8.
#
# Note that Python doesn't support UTF-1!
# This is useful to test the "we don't support this encoding" logic.
# 100% coverage without pragma nocover, here we come!

script = """
# This file is encoded using "{encoding}",
# and starts with the appropriate BOM.

print('Hello, {city}!')
print('Chipmunk 🐿️!')
""".strip() + "\n"

for (encoding, use_encoding, bom, city, valid) in (
    ('gb18030', 'gb18030', b"\x84\x31\x95\x33", "Beijing", True),
    ('utf-1', 'utf-8', b"\xF7\x64\x4C", "Mountain View", False),
    ('utf-7', 'utf-7', b"\x2b\x2f\x76", "Mountain View", True),
    ):

    bytes = script.format(encoding=encoding, city=city).encode(use_encoding)
    invalid_prefix = "" if valid else "invalid_"
    filename = f"{invalid_prefix}{encoding}_bom.py"

    with open(filename, "wb") as f:
        f.write(bom)
        f.write(bytes)
