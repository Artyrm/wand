#!/usr/bin/python

import select
import sys

import json

from time import time

from src_py.input_generator import InputGenerator as Ig
from c_wrap import set_sm_data

KNOWLEDGE = 'generation_knowledge.json'

BLINK_TIME = 1

FEEDBACK = {'calibration': (100, 100, 0, 0),
            "done_0": (0, 0, 0, 30),
            "done_1": (0, 0, 0, 100),
            "done_2": (255, 255, 255, 65),
            "done_3": (255, 0, 0, 65),
            "done_4": (255, 255, 0, 65),
            "done_5": (255, 0, 255, 65),
            "done_6": (255, 255, 255, 65),
            "done_7": (255, 127, 0, 65),
            "done_8": (0, 255, 0, 65),
            'none': (10, 10, 10, 0)}


class DualSM(object):

    def __init__(self):
        super(DualSM, self).__init__()

        with open(KNOWLEDGE, 'r') as f:
            self.knowledge = json.load(f)

        self.states = {value: key for key, value
                       in self.knowledge['states'].items()}

        self.input_generator = Ig(serial_port='/dev/tty.usbmodem1411',
                                  dual=True,
                                  gyro_remap=lambda g: [g[1], -g[0], g[2]])

        self.set_accessible()

    def set_accessible(self, accessible=[0, 1, 2, 3, 4, 5, 6, 7, 8]):
        self.access = sum([2 ** x for x in accessible])

    def run(self):
        reset_time = 0
        for sensor_data in self.input_generator(True):
            device_id = sensor_data['device_id']

            if device_id == 1:
                continue

            result = set_sm_data(device_id,
                                 sensor_data['delta'],
                                 sensor_data['acc'],
                                 sensor_data['gyro'],
                                 sensor_data['mag'],
                                 self.access)

            decoded_result = self.states[result]
            if decoded_result not in ('idle', 'calibration'):
                print device_id, decoded_result

            now = time()

            if (decoded_result in FEEDBACK):
                self.input_generator.set_feedback(device_id,
                                                  FEEDBACK[decoded_result])

                self.input_generator.set_feedback(1 - device_id,
                                                  FEEDBACK[decoded_result])

                reset_time = now + BLINK_TIME

            if (now > reset_time):
                self.input_generator.set_feedback(device_id, FEEDBACK['none'])
                self.input_generator.set_feedback(1 - device_id,
                                                  FEEDBACK['none'])

            if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
                self.input_generator.in_loop = False
        print 'that\'s all'

if __name__ == '__main__':
    dsm = DualSM()
    dsm.run()