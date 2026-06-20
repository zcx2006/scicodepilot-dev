from __future__ import print_function

from youtube_dl.utils import unescapeHTML


source = '&#x110000;'
expected = '&#x110000;'

print('Bug 28 minimal reproduction')
print('input   =', repr(source))

result = unescapeHTML(source)

print('actual  =', repr(result))
print('expected=', repr(expected))

if result != expected:
    raise AssertionError(
        'Invalid numeric HTML entity was not preserved: '
        'expected {!r}, got {!r}'.format(expected, result)
    )

print('PASS: invalid numeric HTML entity was preserved')
