#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Eny sample Post to IFTTT maker channel. """

from __future__ import print_function
import argparse
import serial
import json
import urllib2
import eny


def post_ifttt(event, key, eny_obj, mode):
    """Post to IFTTT"""

    uri = "https://maker.ifttt.com/trigger/{0}/with/key/{1}".format(event, key)
    params = {
        'value1': eny_obj.id,
        'value2': eny_obj.cumulated,
        'value3': mode,
    }
    req = urllib2.Request(uri)
    req.add_header('Content-Type', 'application/json')
    print('Post to IFTTT : {0}'.format(params))
    res = urllib2.urlopen(req, data=json.dumps(params))
    print(res.read())


def main():
    """main"""
    parser = argparse.ArgumentParser(description='Post to IFTTT')
    parser.add_argument(
        'key',
        type=str,
        help='Maker channel secret key')
    parser.add_argument(
        '--event',
        type=str,
        default='eny',
        help='IFTTT event name'
    )
    args = parser.parse_args()

    def single_click(eny_obj):
        """Single click handler"""
        post_ifttt(args.event, args.key, eny_obj, 'single')

    def double_click(eny_obj):
        """Double click handler"""
        post_ifttt(args.event, args.key, eny_obj, 'double')

    port = eny.get_port_names()[0]
    with serial.Serial(port, 115200) as uart:
        # eny.handle_click(uart, single_click)
        eny.handle_double_click(uart, single_click, double_click)
        uart.close()

if __name__ == '__main__':
    main()
