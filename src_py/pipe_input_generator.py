#!/usr/bin/env python
# -*- coding: utf8 -*-

import serial

from time import sleep

SERIAL_PORT = '/dev/tty.usbmodem1411'

BAUDE_RATE = 115200
BUFFER_DELIMITER = '\r\n'

TIME_SCALE = 0.0001  # s/digit

TIME_STAMP_RANGE = 2 ** 16


class InputGenerator(object):
    def __init__(self):
        super(InputGenerator, self).__init__()

    def get_data(self):
        self.data_buffer += self.serial.read(self.serial.inWaiting())

        if self.data_buffer == '':
            return

        data_pieces = self.data_buffer.split(BUFFER_DELIMITER)

        # Put incomplete piece back to the buffer
        self.data_buffer = data_pieces.pop(-1)

        if not data_pieces:
            return

        for line in data_pieces:
            yield self.parse_line(line)

    def parse_line(self, line):
        data = [float(value) for value in line.replace(";", "").split()]
        time_stamp = data[0]

        delta = (0 if self.prev_timestamp is None
                 else time_stamp - self.prev_timestamp)

        self.prev_timestamp = time_stamp

        delta = delta + TIME_STAMP_RANGE if delta < 0 else delta

        data[0] = delta * TIME_SCALE

        return {"delta": data[0],
                "acc": data[1:4],
                "mag": data[4:7],
                "gyro": data[7:10]}

    def __call__(self, from_uart=False, path='', realtime=True):
        self.in_loop = True

        if from_uart:
            self.serial = serial.Serial(SERIAL_PORT, BAUDE_RATE, timeout=0)

            self.data_buffer = ''

            self.prev_timestamp = None

            while self.in_loop:
                for data in self.get_data():
                    yield data
                sleep(0.05)
        else:
            with open(path, 'r') as f:
                for line in f:
                    if not self.in_loop:
                        raise GeneratorExit

                    data = map(float, line.split())
                    if realtime:
                        sleep(data[0])
                    yield {'delta': data[0],
                           'acc': data[1:4],
                           'mag': data[4:7],
                           'gyro': data[7:10]}

    def stop(self):
        self.in_loop = False
