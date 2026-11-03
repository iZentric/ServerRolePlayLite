#!/usr/bin/env python3
"""No game launch; prove known entity IDs, count gate, static safe commands."""
from fc_parked_vehicle_ab import VEHICLES, confirmed_vehicle_count, vehicle_commands


def rejected(text):
    try:
        confirmed_vehicle_count(text)
    except ValueError:
        return
    raise AssertionError('bad entity count accepted')


def main():
    cmds = vehicle_commands()
    cars = [x for x in cmds if x.startswith('summon ')]
    assert len(cars) == VEHICLES
    assert all(x.startswith('summon vehicle:smart_car ') for x in cars)
    assert len(set(cars)) == VEHICLES
    assert not any('127.0.0.1' in x or 'op ' in x for x in cmds)
    assert confirmed_vehicle_count('[Server: #cars has 16 [fcbench]]') == VEHICLES
    assert confirmed_vehicle_count('#cars has 16 [fcbench]\n#cars has 16 [fcbench]',
                                   snapshots=2) == VEHICLES
    for bad in ('', 'Summoned new Smart Car', '#cars has 15 [fcbench]',
                '#cars has 16 [fcbench]\n#cars has 15 [fcbench]'):
        rejected(bad)
    print('PASS: 16 distinct parked modded vehicles, count gate requires exact server scoreboard')


if __name__ == '__main__':
    main()
