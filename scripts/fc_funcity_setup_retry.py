#!/usr/bin/env python3
"""Safely decide whether a Gradle setup failure is worth ONE bounded retry.

Never prints raw log lines, paths, repository URLs or credentials. A second
failure is final even if retryable; the workflow enforces that bound.
"""
import re
import sys
from pathlib import Path

RETRY = re.compile(
    r'(?i)(?:unknownhostexception|sslhandshakeexception|read timed out|'
    r'connection refused|connection reset|could not get resource|'
    r'could not resolve all files|status code:?(?: 429| 50[0234])|'
    r'received status code (?:429|50[0234]))'
)
PERMANENT = re.compile(
    r'(?i)(?:\b(?:401|403|404)\b|plugin .* was not found|'
    r'error: cannot find symbol|outofmemoryerror|no space left on device|'
    r'unsupportedclassversionerror|failed to apply patch)'
)


def retryable(text):
    # Check only the final failure; wrapper URLs in progress output are not a
    # diagnosis. Fail closed on auth/not-found/compile/resource errors.
    tail = text[-30_000:]
    return bool(RETRY.search(tail)) and not bool(PERMANENT.search(tail))


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(2)
    try:
        text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')
    except OSError:
        print('SETUP_RETRY_REJECTED: log unavailable', file=sys.stderr)
        sys.exit(2)
    allowed = retryable(text)
    print('SETUP_RETRY_' + ('TRANSIENT_DEPENDENCY_FAILURE' if allowed else 'NOT_SAFE'))
    sys.exit(0 if allowed else 2)
