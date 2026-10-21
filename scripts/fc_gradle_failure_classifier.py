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
    low = text.lower()[-600_000:]
    hits = [name for name, patterns in CATEGORIES.items()
            if any(re.search(pattern, low) for pattern in patterns)]
    # Categories only; logs may carry secret URLs, so NEVER echo source lines.
    return ','.join(hits) if hits else 'UNCLASSIFIED'


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(2)
    text = Path(sys.argv[1]).read_text(encoding='utf-8', errors='replace')
    print('::error title=FunCity source build safe diagnosis::CATEGORIES=' + classify(text) +
          '; no raw CI log, download URL or credentials published')
