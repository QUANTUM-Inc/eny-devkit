#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Eny command"""

from __future__ import print_function
import argparse
import glob
import collections
import sys
import re
import serial
import threading

__version__ = '0.5.0'

Eny = collections.namedtuple('Eny', 'id cumulated')
RESULT_CODE = {
    '00': 'Success',
    '02': 'Too few arguments',
    '03': 'Too many arguments',
    '05': 'Invalid value',
    '07': 'Table full',
    '08': 'Already registerd',
}


class DoubleClick(object):
    """Check double click."""

    def __init__(self, single_click, double_click, wait_time=1.0):
        self.single_click = single_click
        self.double_click = double_click
        self.wait_time = wait_time
        self.timer = threading.Timer(self.wait_time, self.on_timer)
        self.last = None

    def on_click(self, eny_obj):
        """Click handler"""
        if self.last is not None and self.last.id == eny_obj.id:
            # 2
            self.double_click(eny_obj)
            self.last = None
            self.timer.cancel()
        else:
            if self.last is not None and self.last.id != eny_obj.id:
                self.single_click(self.last)
            self.last = eny_obj
            self.timer.cancel()
            self.timer = threading.Timer(self.wait_time, self.on_timer)
            self.timer.start()

    def on_timer(self):
        """timer"""
        self.single_click(self.last)
        self.last = None


def parse(line):
    """Parse string from eny serial
    Args:
        line (str): The UART text
    Returns:
        Eny: Eny named tuple
    """
    line = str(line)
    if not line.startswith('rcv ok : '):
        return None

    line = line.replace('rcv ok : ', '')
    line = line.translate(None, ' ')
    line = line.translate(None, '\r\n')

    pairs = line.split(',')
    if len(pairs) < 3:
        return None

    kvs = dict(pair.split('=') for pair in pairs)
    return Eny(id=kvs['cid'],
               cumulated=int(kvs['cum_no'], 16))


def get_port_names():
    """Returns available serial ports."""
    if sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/ttyUSB*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.usbserial*')
    else:
        raise EnvironmentError('Unsupported platform')
    if len(ports) is 0:
        raise EnvironmentError('eny not connected')
    return ports


def handle_click(uart, handler):
    """Listen eny event"""
    try:
        print(u'Ctl-c to exit')
        while True:
            line = uart.readline()
            eny_obj = parse(line)
            if eny_obj != None:
                handler(eny_obj)
    except KeyboardInterrupt:
        print(u' - Quitting')


def handle_double_click(uart, single_click, double_click, wait_time=0.8):
    """Listen eny event with Double click"""
    handler = DoubleClick(single_click, double_click, wait_time)
    handle_click(uart, handler.on_click)


def main():
    """Eny command line"""

    args = _init_parser()
    if args.port is None:
        args.port = get_port_names()[0]

    cmd = args.which
    if cmd == 'pair add':
        cmd += ' ' + args.device_id
    elif cmd == 'pair del':
        cmd += ' ' + str(args.device_index)

    with serial.Serial(args.port, args.baudrate) as uart:
        if cmd == 'listen':
            handle_click(uart, print)
        else:
            has_result_code = re.compile(r'pair add|del|reset')
            uart.write(cmd + '\r\n')
            uart.timeout = 0.5
            line = None
            while line != '':
                line = uart.readline()
                if line == '\r' or len(line) is 0:
                    continue
                elif has_result_code.search(cmd) is not None:
                    code = line.split(' ')[0]
                    print(RESULT_CODE[code])
                else:
                    print(line)
            uart.flush()
        uart.close()


def _init_parser():
    """Initialize argument parser"""
    parser = argparse.ArgumentParser(description='Eny client')
    # eny -port /dev/ttyUSB*
    parser.add_argument(
        '--port',
        default=None,
        type=str,
        nargs=1,
        help='Port name like /dev/ttyUSB*')
    # eny -baudrate 115200
    parser.add_argument(
        '--baudrate',
        default=115200,
        type=int,
        nargs=1,
        help='baudrate, default: %(default)s')

    sub = parser.add_subparsers()
    # eny get_id
    get_id = sub.add_parser(
        'get_id',
        description='Shown own TX ID. ID is 8-digit hexadecimal number.')
    get_id.set_defaults(which='get_id')
    # eny listen
    listen = sub.add_parser(
        'listen',
        description='Listen raw UART')
    listen.set_defaults(which='listen')

    # eny pair
    pair = sub.add_parser(
        'pair',
        description='Pair commands').add_subparsers()
    # eny pair view
    pair_view = pair.add_parser(
        'view',
        description='Shown current pairing list.')
    pair_view.set_defaults(which='pair view')
    # eny pair add FFFFFFFF
    pair_add = pair.add_parser(
        'add',
        description='Add a pairing ID to the pairing list.'
        + ' (Then need a vcant space of the list.)')
    pair_add.set_defaults(which='pair add')
    pair_add.add_argument(
        'device_id',
        type=str,
        help='ID is 8-digit hexadecimal number.(00000001~fffffffe)')
    # eny pair del 31
    pair_del = pair.add_parser(
        'del',
        description='Delete a pairing ID from the pairing lsit.')
    pair_del.set_defaults(which='pair del')
    pair_del.add_argument(
        'device_index',
        type=int,
        choices=range(0, 32),
        help='Input is a table number.(0~31)')
    # eny pair reset
    pair_reset = pair.add_parser(
        'reset',
        description='Reset pair list')
    pair_reset.set_defaults(which='pair reset')
    return parser.parse_args()


if __name__ == '__main__':
    main()
