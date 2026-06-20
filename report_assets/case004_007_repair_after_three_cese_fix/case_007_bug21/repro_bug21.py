from __future__ import print_function

from youtube_dl.utils import urljoin


cases = [
    (
        'bytes path',
        'https://example.com/root/',
        b'video/page.html',
        'https://example.com/root/video/page.html',
    ),
    (
        'bytes base',
        b'https://example.com/root/',
        'video/page.html',
        'https://example.com/root/video/page.html',
    ),
    (
        'bytes base and path',
        b'https://example.com/root/',
        b'video/page.html',
        'https://example.com/root/video/page.html',
    ),
]

failures = []

print('Bug 21 minimal reproduction')

for name, base, path, expected in cases:
    actual = urljoin(base, path)

    print()
    print('case    =', name)
    print('base    =', repr(base))
    print('path    =', repr(path))
    print('actual  =', repr(actual))
    print('expected=', repr(expected))

    if actual != expected:
        failures.append(
            '{}: expected {!r}, got {!r}'.format(
                name, expected, actual
            )
        )

if failures:
    raise AssertionError(
        'Bytes URL handling failed:\n- ' + '\n- '.join(failures)
    )

print('PASS: bytes base/path values were decoded and joined correctly')
