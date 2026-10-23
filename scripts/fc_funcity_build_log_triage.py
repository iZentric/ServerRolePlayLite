#!/usr/bin/env python3
"""Classify a CatServer source build log WITHOUT printing its raw contents.

This is exclusively for a GitHub-hosted source build of pinned public upstream
code. No world/mod/plugin/client files, private paths, server logs, or artifacts.
"""
import re
import sys
from pathlib import Path

ERRORS = {
    'MISSING_SYMBOL': r'cannot find symbol',
    'MISSING_PACKAGE': r'package [\w.]+ does not exist',
    'WRONG_TYPE': r'incompatible types',
    'MAPPING_FAILURE': r'(failed to apply patch|no mapping|missing.*mapping)',
    'DEPENDENCY_FETCH': r'(could not resolve|could not get resource|read timed out|unknownhostexception)',
    'GRADLE_TASK_DEPENDENCY': r'(uses this output of task|without declaring an explicit dependency)',
    'GRADLE_DAEMON_LOST': r'(gradle build daemon disappeared|daemon has disappeared)',
    'RESOURCE_EXHAUSTED': r'(outofmemoryerror|java heap space|no space left on device|oom killer)',
    'JAVA_VERSION': r'(unsupportedclassversionerror|invalid source release|unrecognized vm option)',
    'KOTLIN_OR_GROOVY': r'(could not compile build file|startup failed:)',
}


def triage(text):
    tail = text[-100_000:]
    tasks = re.findall(r'(?m)^> Task (:[A-Za-z0-9_:.-]+) FAILED\s*$', tail)
    # The Gradle distribution URL during setup does not explain :forge:compileJava.
    task = tasks[-1] if tasks else 'UNKNOWN'
    labels = [name for name, pattern in ERRORS.items() if re.search(pattern, tail, re.I)]
    if not labels:
        labels = ['UNKNOWN_FAILURE']
    # Only names seen in the pinned *public* source; no paths, log lines,
    # messages, URLs, usernames, tokens, filenames of private pack content.
    symbols = sorted(set(re.findall(r'(?m)^\s*symbol:\s*(?:class|variable|method)\s+([A-Za-z][A-Za-z0-9_]{0,79})', tail)))[:8]
    symbols = [s for s in symbols if not re.search(r'(secret|token|password|key|auth)', s, re.I)]
    return task, ','.join(labels), ','.join(symbols) or 'NONE'


def main(path):
    text = Path(path).read_text(encoding='utf-8', errors='replace')
    task, labels, symbols = triage(text)
    # Task is upstream-generated Gradle identifier matched above, not raw text.
    print(f'SOURCE_BUILD_TRIAGE task={task} categories={labels} upstream_symbols={symbols}')
    return 0


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
