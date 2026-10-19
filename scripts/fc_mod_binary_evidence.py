#!/usr/bin/env python3
"""Read-only, bounded Forge mod metadata from a SHA-verified historical server ZIP.

No world, configs, launch, publishing or downloads. Do not treat JAR presence as
proof of loaded dependencies or performance. Intended for the hosted audit job.
"""
import argparse
import io
import json
import re
import tomllib
import zipfile

FOCUS = (
    'Pizzaland_v68.jar', 'Modernxl 1.16.5.jar',
    'Placebo-1.16.5-4.7.1.jar', 'incontrol-1.16-5.2.12.jar',
    'Ksyxis-1.4.6.jar', 'FastSuite-1.16.4-1.1.1.jar',
    'FastWorkbench-1.16.5-4.6.2.jar', 'roadstuff-1.16.5-4.3.0.jar',
    'mapperbase-1.16.5-2.4.0.0.jar', 'pamhc2foodcore-1.16.3-1.0.2.jar',
)
SAFE = re.compile(r'[^a-zA-Z0-9 ._+/-]')


def safe(value):
    return SAFE.sub('_', str(value))[:100]


def inspect_jar(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as jar:
        info = jar.infolist()
        if len(info) > 100_000:
            raise ValueError('excessive number of JAR entries')
        names = {i.filename for i in info}
        classes = sum(i.filename.endswith('.class') for i in info)
        assets = sum(i.filename.startswith('assets/') and not i.is_dir() for i in info)
        toml_name = next((x for x in ('META-INF/mods.toml', 'META-INF/MODS.TOML') if x in names), None)
        result = {'metadata': 'absent', 'mod_ids': [], 'display_names': [],
                  'declared_dependencies': {}, 'required_dependencies': {},
                  'classes': classes, 'asset_files': assets, 'jar_bytes': len(raw)}
        if toml_name:
            metadata = jar.getinfo(toml_name)
            if metadata.file_size > 200_000:
                raise ValueError('oversized mods.toml')
            try:
                data = tomllib.loads(jar.read(toml_name).decode('utf-8-sig'))
            except (ValueError, UnicodeError):
                result['metadata'] = 'unparsed_mods.toml'
                return result
            result['metadata'] = 'mods.toml'
            result['mod_ids'] = [safe(m.get('modId', '')) for m in data.get('mods', [])]
            result['display_names'] = [safe(m.get('displayName', '')) for m in data.get('mods', [])]
            result['declared_dependencies'] = {
                safe(mod): [safe(dep.get('modId', '')) for dep in deps]
                for mod, deps in data.get('dependencies', {}).items()
            }
            result['required_dependencies'] = {
                safe(mod): [safe(dep.get('modId', '')) for dep in deps
                            if dep.get('mandatory') is True]
                for mod, deps in data.get('dependencies', {}).items()
            }
        elif 'mcmod.info' in names:
            result['metadata'] = 'legacy_mcmod.info'
        return result


def inspect_archive(path, focus=FOCUS):
    with zipfile.ZipFile(path) as source:
        found = {}
        for info in source.infolist():
            name = info.filename.split('/')[-1]
            if name not in focus or info.is_dir() or '/mods/' not in '/' + info.filename:
                continue
            if name in found or info.file_size > 300_000_000:
                raise ValueError('ambiguous or oversized source JAR: ' + name)
            found[name] = inspect_jar(source.read(info))
        missing = set(focus) - found.keys()
        if missing:
            raise ValueError('source JAR(s) missing: ' + ', '.join(sorted(missing)))
        return found


def scan_required_dependents(path, mod_id):
    """Inspect embedded JAR declarations, not optional remote files or runtime uses."""
    dependents, unknown, inspected = [], [], 0
    with zipfile.ZipFile(path) as archive:
        jar_entries = [i for i in archive.infolist() if not i.is_dir() and
                       i.filename.casefold().endswith('.jar') and
                       ('/mods/' in '/' + i.filename.casefold())]
        if len(jar_entries) > 64:
            raise ValueError('too many embedded JARs')
        for info in jar_entries:
            if info.file_size > 300_000_000:
                raise ValueError('oversized source JAR')
            record = inspect_jar(archive.read(info))
            inspected += 1
            name = safe(info.filename.split('/')[-1])
            if record['metadata'] != 'mods.toml':
                unknown.append(name)
            if any(mod_id in deps for deps in record['required_dependencies'].values()):
                dependents.append(name)
    return {'embedded_jars_inspected': inspected, 'mandatory_dependents': sorted(dependents),
            'metadata_not_parsed': sorted(unknown),
            'limits': 'embedded JAR declarations only, not remote files or runtime uses'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('server_zip')
    args = parser.parse_args()
    result = inspect_archive(args.server_zip)
    for name in FOCUS:
        record = json.dumps({'jar': name, **result[name]}, ensure_ascii=True, sort_keys=True)
        print(record)
        # Actions logs may be unreachable from the sandbox; check-run notices are
        # also retrievable through the GitHub API. Values are metadata-only/sanitized.
        print(f'::notice title=Jar metadata {safe(name)}::{record}')


if __name__ == '__main__':
    main()
