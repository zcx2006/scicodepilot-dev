from __future__ import print_function

from youtube_dl.utils import urljoin


base = None
path = 'rtmp://media.example.com/live/stream'
expected = path

print('Bug 13 minimal reproduction')
print('base    =', repr(base))
print('path    =', repr(path))

actual = urljoin(base, path)

print('actual  =', repr(actual))
print('expected=', repr(expected))

if actual != expected:
    raise AssertionError(
        'Absolute URL with a non-HTTP scheme was handled incorrectly: '
        'expected {!r}, got {!r}'.format(expected, actual)
    )

print('PASS: non-HTTP absolute URL was preserved')
