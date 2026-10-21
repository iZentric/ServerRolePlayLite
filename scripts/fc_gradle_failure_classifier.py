#!/usr/bin/env python3
"""Publish only fixed categories from a private CI Gradle log, never raw lines."""
import re
import sys
from pathlib import Path

CATEGORIES = {
    'GRADLE_DISTRIBUTION': (r'gradle-[\d.]+-bin\.zip', r'gradle wrapper.*(download|fail)'),
    'GRADLE_PLUGIN': (r'plugin .* was not found', r'could not resolve.*gradle:',
                      r'could not find.*forgegradle'),
    'JAVA_TOOLCHAIN': (r'no matching toolchains found', r'toolchain.*not.*found',
                        r'unrecognized vm option', r'java.*version.*unsupported'),
    'DEPENDENCY_NETWORK': (r'could not get resource', r'could not resolve all files',
                            r'unknownhostexception', r'sslhandshakeexception',
                            r'read timed out', r'connection refused'),
    'SOURCE_COMPILE': (r'compilation failed', r'error: cannot find symbol',
                       r'error: package .* does not exist'),
    'PATCH_SETUP': (r'genserverbinpatches.*failed', r'setupmcp.*failed',
                     r'failed to apply patch'),
    'RESOURCE_LIMIT': (r'outofmemoryerror', r'no space left on device',
                        r'killed.*(137|oom)'),
}


def classify(text):
    # Prioritize the final failure, not benign download/progress text at the start.
    low = text.lower()[-30_000:]
    hits = [name for name, patterns in CATEGORIES.items()
            if any(re.search(pattern, low) for pattern in patterns)]
    return ','.join(hits) if hits else 'UNCLASSIFIED'


def details(text):
    tail = text[-30_000:]
    failed = re.findall(r'(?m)^> Task (:[A-Za-z0-9_:.-]+) FAILED', tail)
    task = failed[-1] if failed else 'UNKNOWN'
    markers = {
        'JVM_OPTION': 'Unrecognized VM option',
        'NO_TOOLCHAIN': 'No matching toolchains found',
        'MISSING_SYMBOL': 'cannot find symbol',
        'INVALID_SOURCE': 'invalid source release',
        'MISSING_PACKAGE': 'does not exist',
        'INCOMPATIBLE_TYPE': 'incompatible types',
        'UNSUPPORTED_CLASS': 'UnsupportedClassVersionError',
        'RESOLVE_DEPENDENCY': 'Could not resolve all files',
        'NOT_ENOUGH_MEMORY': 'OutOfMemoryError',
    }
    flags = [name for name, needle in markers.items() if needle.lower() in tail.lower()]
    # Task is public upstream source identifier only. No raw lines or URLs.
    packages = sorted(set(re.findall(r'error: package ([A-Za-z][A-Za-z0-9_.]+) does not exist', tail)))[:5]
    symbols = sorted(set(re.findall(r'(?m)^\s*symbol:\s*(?:class|variable|method)\s+([A-Za-z][A-Za-z0-9_]+)', tail)))[:5]
    return task, ','.join(flags) if flags else 'NONE', ','.join(packages) or 'NONE', ','.join(symbols) or 'NONE'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(2)
    text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')
    task, flags, packages, symbols = details(text)
    print('::error title=FunCity source build safe diagnosis::CATEGORIES=' + classify(text) +
          ' FAILED_TASK=' + task + ' FLAGS=' + flags +
          ' PUBLIC_UPSTREAM_PACKAGES=' + packages + ' PUBLIC_UPSTREAM_SYMBOLS=' + symbols +
          '; no raw CI log, download URL or credentials published')
