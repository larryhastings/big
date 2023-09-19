#!/usr/bin/env python3

#
# This script parses the Unicode database,
# specifically the XML version.
#
# To run this script, you'll need to locally install
# the Unicode XML database.
#
#     Go to this URL:
#            https://www.unicode.org/Public/
#     Then click on the directory for the version you want,
#     probably the current version.  As of this writing the
#     current version is 15.1.0.
#
#     Then click on the "ucdxml" directory.
#
#     Download the "ucd.all.flat.zip" file  and unzip it.
#     It should only contain one file, "ucd.all.flat.xml".
#     Copy that file into the same directory as this script.
#

# If you do that, you should see this output:
expected_output = """
A canonical list of all Unicode whitespace and line-breaking characters.

Unicode whitespace:

    char    decimal  unicode  description
    --------------------------------------------------
    '\t'          9   U+0009  CHARACTER TABULATION
    '\n'         10   U+000A  LINE FEED (LF)
    '\v'         11   U+000B  LINE TABULATION
    '\f'         12   U+000C  FORM FEED (FF)
    '\r'         13   U+000D  CARRIAGE RETURN (CR)
    ' '          32   U+0020  SPACE
    '\x85'      133   U+0085  NEXT LINE (NEL)
    '\xa0'      160   U+00A0  NON-BREAKING SPACE
    '\u1680'   5760   U+1680  OGHAM SPACE MARK
    '\u2000'   8192   U+2000  EN QUAD
    '\u2001'   8193   U+2001  EM QUAD
    '\u2002'   8194   U+2002  EN SPACE
    '\u2003'   8195   U+2003  EM SPACE
    '\u2004'   8196   U+2004  THREE-PER-EM SPACE
    '\u2005'   8197   U+2005  FOUR-PER-EM SPACE
    '\u2006'   8198   U+2006  SIX-PER-EM SPACE
    '\u2007'   8199   U+2007  FIGURE SPACE
    '\u2008'   8200   U+2008  PUNCTUATION SPACE
    '\u2009'   8201   U+2009  THIN SPACE
    '\u200a'   8202   U+200A  HAIR SPACE
    '\u2028'   8232   U+2028  LINE SEPARATOR
    '\u2029'   8233   U+2029  PARAGRAPH SEPARATOR
    '\u202f'   8239   U+202F  NARROW NO-BREAK SPACE
    '\u205f'   8287   U+205F  MEDIUM MATHEMATICAL SPACE
    '\u3000'  12288   U+3000  IDEOGRAPHIC SPACE

Unicode line-breaking whitespace:

    char    decimal  unicode  description
    --------------------------------------------------
    '\n'         10   U+000A  LINE FEED (LF)
    '\v'         11   U+000B  LINE TABULATION
    '\f'         12   U+000C  FORM FEED (FF)
    '\r'         13   U+000D  CARRIAGE RETURN (CR)
    '\x85'      133   U+0085  NEXT LINE (NEL)
    '\u2028'   8232   U+2028  LINE SEPARATOR
    '\u2029'   8233   U+2029  PARAGRAPH SEPARATOR

-----------------------------------------------------------------

There are no characters considered to be whitespace by Unicode but not by the Python str object.

These characters are considered to be whitespace by the Python str object, but not by Unicode:

    char    decimal  unicode  description
    --------------------------------------------------
    '\x1c'       28   U+001C  INFORMATION SEPARATOR FOUR
    '\x1d'       29   U+001D  INFORMATION SEPARATOR THREE
    '\x1e'       30   U+001E  INFORMATION SEPARATOR TWO
    '\x1f'       31   U+001F  INFORMATION SEPARATOR ONE

ASCII and the Python bytes object agree on the list of whitespace characters.

There are no characters considered to be line-breaking whitespace by Unicode but not by the Python str object.

These characters are considered to be line-breaking whitespace by the Python str object, but not by Unicode:

    char    decimal  unicode  description
    --------------------------------------------------
    '\x1c'       28   U+001C  INFORMATION SEPARATOR FOUR
    '\x1d'       29   U+001D  INFORMATION SEPARATOR THREE
    '\x1e'       30   U+001E  INFORMATION SEPARATOR TWO

These characters are considered to be line-breaking whitespace by ASCII, but not by the Python bytes object:

    char    decimal  unicode  description
    --------------------------------------------------
    '\v'         11   U+000B  LINE TABULATION
    '\f'         12   U+000C  FORM FEED (FF)

There are no characters considered to be line-breaking whitespace by the Python bytes object but not by ASCII.
"""



import xml.etree.ElementTree as et

ucd = et.parse("ucd.all.flat.xml").getroot()

#
# lb definitions gleaned from:
#   Unicode Standard Annex #14
#   UNICODE LINE BREAKING ALGORITHM
#
#   https://www.unicode.org/reports/tr14/tr14-32.html
#
lb_linebreaks = {
    'BK': 'Mandatory Break - Cause a line break (after)',
    'CR': 'Carriage Return - Cause a line break (after), except between CR and LF',
    'LF': 'Line Feed - Cause a line break (after)',
    'NL': 'Next Line - Cause a line break (after)',
}

lb_not_linebreaks = {
    'CM': 'Combining Mark - Prohibit a line break between the character and the preceding character',
    'SG': 'Surrogate - Do not occur in well-formed text',
    'WJ': 'Word Joiner - Prohibit line breaks before and after',
    'ZW': 'Zero Width Space - Provide a break opportunity',
    'GL': 'Non-breaking ("Glue") - Prohibit line breaks before and after',
    'SP': 'Space - Enable indirect line breaks',

    'B2': 'Break Opportunity Before and After - Provide a line break opportunity before and after the character',
    'BA': 'Break After - Generally provide a line break opportunity after the character',
    'BB': 'Break Before - Punctuation used in dictionaries    Generally provide a line break opportunity before the character',
    'HY': 'Hyphen - Provide a line break opportunity after the character, except in numeric context',
    'CB': 'Contingent Break Opportunity -Provide a line break opportunity contingent on additional information',
    }

# The Python parser understands \v for vertical tab and \f for form feed.
# But the repr for str objects doesn't convert back to those.
# I prefer lookin' at 'em, and it's my script, so I do this conversion myself.
special_char_reprs = {
    "\x0b": "'\\v'",
    "\x0c": "'\\f'",
    }

def special_char_repr(c):
    return special_char_reprs.get(c, repr(c))

unicode_whitespace = []
unicode_linebreaks = []

ascii_whitespace = []
ascii_linebreaks = []

str_whitespace = []
str_linebreaks = []

bytes_whitespace = []
bytes_linebreaks = []


for item in ucd.iter():
    tag = item.tag.rpartition('}')[2]
    if tag != 'char':
        continue

    code_point = item.attrib.get('cp')
    if not code_point:
        # not a character.
        # the database has other entries, e.g. ranges (defined via "first-cp" through "last-cp")
        continue

    lb = item.attrib['lb']
    description = item.attrib['na1'] or item.attrib['na']

    i = int(code_point.lstrip('0') or '0', 16)
    c = chr(i)
    repr_c = special_char_repr(c).ljust(8)
    formatted = f"    {repr_c} {i:>6}   U+{code_point}  {description}"
    t = (i, formatted)


    is_unicode_whitespace = item.attrib['WSpace'] == 'Y'
    is_unicode_linebreak = lb_linebreaks.get(lb)

    if is_unicode_whitespace:
        unicode_whitespace.append(t)
        if is_unicode_linebreak:
            unicode_linebreaks.append(t)
    else:
        assert not is_unicode_linebreak, "Unicode says this character is a linebreak but not whitespace!{formatted}"


    test_string = f"a{c}b"
    is_str_whitespace = len(test_string.split()) == 2
    is_str_linebreak = len(test_string.splitlines()) == 2

    if is_str_whitespace:
        str_whitespace.append(t)
        if is_str_linebreak:
            str_linebreaks.append(t)
    else:
        assert not is_str_linebreak, "The Python str object says this character is a linebreak but not whitespace!{formatted}"


    defined_for_ascii = i < 128
    if defined_for_ascii:
        test_bytes = test_string.encode('ascii')
        is_bytes_whitespace = len(test_bytes.split()) == 2
        is_bytes_linebreak = len(test_bytes.splitlines()) == 2
        if is_bytes_whitespace:
            bytes_whitespace.append(t)
            if is_bytes_linebreak:
                bytes_linebreaks.append(t)
        else:
            assert not is_bytes_linebreak, "The Python bytes object says this character is a linebreak but not whitespace!{formatted}"

        if is_unicode_whitespace:
            ascii_whitespace.append(t)
            if is_unicode_linebreak:
                ascii_linebreaks.append(t)

assert unicode_whitespace
assert unicode_linebreaks
assert ascii_whitespace
assert ascii_linebreaks
assert str_whitespace
assert str_linebreaks
assert bytes_whitespace
assert bytes_linebreaks

##############################################################################

print("A canonical list of all Unicode whitespace and line-breaking characters.")
print()

heading = """
    char    decimal  unicode  description
    --------------------------------------------------
""".rstrip('\n')

print("Unicode whitespace:")
print(heading)
for i, s in unicode_whitespace:
    print(s)

print()

print("Unicode line-breaking whitespace:")
print(heading)
for i, s in unicode_linebreaks:
    print(s)
print()

print("-" * 65)
print()

for what, first, first_list, second, second_list in (
    (
        "whitespace",
        "Unicode", unicode_whitespace,
        "the Python str object", str_whitespace,
        ),
    (
        "whitespace",
        "ASCII", ascii_whitespace,
        "the Python bytes object", bytes_whitespace,
        ),
    (
        "line-breaking whitespace",
        "Unicode", unicode_linebreaks,
        "the Python str object", str_linebreaks,
        ),
    (
        "line-breaking whitespace",
        "ASCII", ascii_linebreaks,
        "the Python bytes object", bytes_linebreaks,
        ),
    ):

    first_set = set(first_list)
    second_set = set(second_list)

    if first_set == second_set:
        print(f"{first[0].upper()}{first[1:]} and {second} agree on the list of {what} characters.")
        print()
    else:
        for (a, a_set, b, b_set) in (
            (first, first_set, second, second_set),
            (second, second_set, first, first_set),
            ):
            delta = list(a_set - b_set)
            if not delta:
                print(f"There are no characters considered to be {what} by {a} but not by {b}.")
            else:
                delta.sort()
                print(f"These characters are considered to be {what} by {a}, but not by {b}:")
                print(heading)
                for i, s in delta:
                    print(s)
            print()
