"""Backport one dlint0.15 expression for the required Python3.5 lint gate.

The upstream wheel omits Requires-Python and contains one f-string. Preserve
all rules, release bytes outside that expression, and the real flake8 gate.
"""
import hashlib
import importlib.util
import sys
from pathlib import Path


def main():
    if sys.version_info[:2] != (3, 5):
        raise RuntimeError('This reviewed tool repair is only for Python3.5')
    spec = importlib.util.find_spec('dlint')
    target = Path(spec.origin).parent / 'linters' / 'bad_hashlib_use.py'
    source = target.read_bytes()
    if hashlib.sha256(source).hexdigest() != 'b8f35553e392e8c0fd7a025ecf4285cf8bf50b6dab1e1db19c37dc523bef9943':
        raise RuntimeError('Unexpected dlint source; upstream review required')
    before = b'f"hashlib.{hash_algorithm}"'
    after = b'"hashlib.{}".format(hash_algorithm)'
    if source.count(before) != 1:
        raise RuntimeError('Expected exactly one reviewed f-string')
    target.write_bytes(source.replace(before, after))
    print('dlint35_compat=pass release=0.15.0 rule_changes=0')


if __name__ == '__main__':
    main()
