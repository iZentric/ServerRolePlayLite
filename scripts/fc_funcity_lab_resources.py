#!/usr/bin/env python3
"""Fail closed on the effective Linux 2-vCPU/12-GB private lab budget.

This is a resource preflight, NOT a benchmark or proof of player capacity.
It never reads the world, connects to a host or prints private files.
"""
import os
from pathlib import Path
import re
import sys


class LabRejected(ValueError):
    pass


def verify_limits(affinity, cpu_max, ram_limit_mib, available_mib):
    try:
        quota_text, period_text = cpu_max.split()
        period = int(period_text)
        quota = float('inf') if quota_text == 'max' else int(quota_text)
        if (type(affinity) is not int or affinity < 1 or period < 1
                or quota <= 0 or type(ram_limit_mib) is not int
                or type(available_mib) is not int):
            raise ValueError('invalid effective limits')
        effective_cpus = min(affinity, quota / period)
        if (effective_cpus != 2 or not 11400 <= ram_limit_mib <= 12288
                or available_mib < 10240):
            raise ValueError('not the isolated 2-vCPU/12-GB budget with 10 GiB free')
    except (ValueError, TypeError) as exc:
        raise LabRejected('effective 2-vCPU/12-GB lab not verified') from exc
    return True


def optional(path):
    try:
        return Path(path).read_text(encoding='ascii').strip()
    except FileNotFoundError:
        return None


def inspect_host():
    try:
        meminfo = Path('/proc/meminfo').read_text(encoding='ascii')
        def kib(name):
            match = re.search(r'^' + name + r':\s+(\d+) kB$', meminfo, re.MULTILINE)
            if not match:
                raise LabRejected('Linux memory inventory unavailable')
            return int(match.group(1))
        ram_limit = kib('MemTotal') // 1024
        available = kib('MemAvailable') // 1024
        cpu_max = optional('/sys/fs/cgroup/cpu.max')
        if cpu_max is None:
            quota = optional('/sys/fs/cgroup/cpu/cpu.cfs_quota_us')
            period = optional('/sys/fs/cgroup/cpu/cpu.cfs_period_us')
            cpu_max = ((quota if quota and quota != '-1' else 'max') + ' ' + period
                       if period else 'max 100000')
        limit = optional('/sys/fs/cgroup/memory.max')
        usage = optional('/sys/fs/cgroup/memory.current')
        if limit is None:
            limit = optional('/sys/fs/cgroup/memory/memory.limit_in_bytes')
            usage = optional('/sys/fs/cgroup/memory/memory.usage_in_bytes')
        if limit and limit != 'max':
            if usage is None:
                raise LabRejected('cgroup memory usage unavailable')
            limit_bytes = int(limit)
            ram_limit = min(ram_limit, limit_bytes // 1048576)
            available = min(available, max(0, limit_bytes - int(usage)) // 1048576)
        return verify_limits(len(os.sched_getaffinity(0)), cpu_max, ram_limit, available)
    except (OSError, ValueError, AttributeError) as exc:
        raise LabRejected('Linux resource preflight unavailable') from exc


if __name__ == '__main__':
    try:
        inspect_host()
    except LabRejected:
        print('LAB_RESOURCES_REJECTED: no private copy or server was touched', file=sys.stderr)
        sys.exit(2)
    print('LAB_RESOURCES_PASS: 2 vCPU / 12 GB effective, 10 GiB free; no player test')
