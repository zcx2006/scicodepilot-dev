from __future__ import print_function

from youtube_dl.utils import unescapeHTML


source = '&a&quot;'
expected = '&a"'

print('Bug 3 minimal reproduction')
print('input   =', repr(source))

result = unescapeHTML(source)

print('actual  =', repr(result))
print('expected=', repr(expected))

if result != expected:
    raise AssertionError(
        'Malformed HTML entity was decoded incorrectly: '
        'expected {!r}, got {!r}'.format(expected, result)
    )

print('PASS: malformed HTML entity was decoded correctly')
