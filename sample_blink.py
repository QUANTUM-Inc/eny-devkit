#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Eny sample Blink GPIO LED on Raspberry PI """

from __future__ import print_function
import argparse
import serial
import sys
import time
import RPi.GPIO as GPIO
import eny


def main():
    """main"""

    if not sys.platform.startswith('linux'):
        raise EnvironmentError('Unsupported platform')

    parser = argparse.ArgumentParser(description='Samlle blink')
    parser.add_argument(
        '--pin',
        type=int,
        default=21,
        help='GPIO pin to LED+'
    )
    args = parser.parse_args()
    led_pin = args.pin

    def blink(eny_obj):
        """Blink LED"""
        print(eny_obj)
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(led_pin, GPIO.LOW)

    def blink_twice(eny_obj):
        """Blink LED twice"""
        print(eny_obj)
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(led_pin, GPIO.LOW)
        time.sleep(0.3)
        GPIO.output(led_pin, GPIO.HIGH)
        time.sleep(0.3)
        GPIO.output(led_pin, GPIO.LOW)

    # start GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(led_pin, GPIO.OUT)

    port = eny.get_port_names()[0]
    with serial.Serial(port, 115200) as uart:
        # eny.handle_click(uart, blink)
        eny.handle_double_click(uart, blink, blink_twice)
        uart.close()

    GPIO.cleanup()

if __name__ == '__main__':
    main()
