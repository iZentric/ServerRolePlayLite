#!/usr/bin/env python3
"""Generate the static FunCity landing page from its reviewed template.

No network access, live server status, API key or player data is used.
"""
from pathlib import Path

HERE = Path(__file__).resolve().parent
HTML = (HERE / 'template.html').read_text(encoding='utf-8')


def main():
    dest = HERE / 'index.html'
    dest.write_text(HTML, encoding='utf-8')
    print(f'landing page generated: {dest} ({len(HTML.encode("utf-8"))} bytes)')


if __name__ == '__main__':
    main()
