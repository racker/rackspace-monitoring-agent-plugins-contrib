#!/usr/bin/env python
#
# Script for monitoring remaining useful lifetime of OnMetal v1 SATADOM.
#
# Requires the following binaries installed & on path:
#  - smartctl
#  - lsblk
#
# Suggested alarm criteria:
#
# if (metric['percent_pe_cycles_used'] >= 1) {
#     return new AlarmStatus(CRITICAL, 'Drive is beyond expected life.');
# }
#
# if (metric['percent_pe_cycles_used'] >= .8) {
#     return new AlarmStatus(WARNING, 'Drive >= 80% of its expected life.');
# }
#
# return new AlarmStatus(OK, 'Drive less than 80% through its expected life.');

import subprocess
import sys

DEVICE = "/dev/sda"

SATADOM_PE_MAX = {
    '32G MLC SATADOM': 3000,
    '7 PIN  SATA FDM': 3000,
    'Fastable SD 131 7': 3000,
    'Fastable SD131 7': 3000,
    'SATADOM-SH TYPE': 100000,
    'SATADOM-SH TYPE C 3SE': 100000,
}


def _fail(msg="Unknown Error"):
    print("status err {}".format(msg))
    sys.exit(1)


def _get_smartctl_attributes():
    try:
        out = subprocess.check_output(['smartctl', '--attributes', DEVICE])
    except:
        _fail("failed running smartctl")

    header = None
    it = iter(out.split('\n'))
    for line in it:
        # note(JayF): skip forward until we get to the header and pull
        # it out
        if line.strip().startswith('ID#'):
            header = line.strip().split()
            break

    attributes = {}
    # note(JayF): All lines at this point contain metrics or are blank.
    for line in it:
        line = line.strip()
        if not line:
            continue
        linelist = line.split()
        # note(JayF): match up headers to values to generate a dict
        key = linelist[0] + '-' + linelist[1]
        value = dict(zip(header[2:], linelist[2:]))
        attributes[key] = value

    return attributes


def _calculate_pe_cycles(actual_value):
    return int(hex(int(actual_value))[-4:], 16)


def _calculate_life_expectancy(pe_cycle_current, pe_cycle_max):
    # note(JayF): Force one of the values to a float to avoid int division
    return "{:f}".format(pe_cycle_current / float(pe_cycle_max))


def _get_satadom_model():
    try:
        model = subprocess.check_output(
            ['lsblk', '-oMODEL', DEVICE]).strip().split('\n')[1]
    except:
        _fail("failed running lsblk")

    if model not in SATADOM_PE_MAX.keys():
        _fail("UNKNOWN SATADOM MODEL")
        exit(1)
    else:
        return model


attrs = _get_smartctl_attributes()
life_remaining = _calculate_life_expectancy(
    _calculate_pe_cycles(attrs['173-Unknown_Attribute']['RAW_VALUE']),
    SATADOM_PE_MAX[_get_satadom_model()])

print("status ok smart stats gathered successfully")
print("metric percent_pe_cycles_used float {}".format(life_remaining))
