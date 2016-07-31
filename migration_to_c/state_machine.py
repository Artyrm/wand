#!/usr/bin/env python

from os import makedirs, path
from uuid import uuid1

import numpy as np

from src_py.imu import IMU
from src_py.splitter import PipeSplitter
from src_py.sequence_processor import SequenceProcessor


import c_wrap

MODE_TRAIN = 0
MODE_DEMO = 1
MODE_RUN = 2

OUTPUT_MAIN = 0
OUTPUT_WIDGET = 1
OUTPUT_TEST = 2

MODE_VALUES = {'train': MODE_TRAIN, 'demo': MODE_DEMO, 'run': MODE_RUN}
MODE_NAMES = {value: key for key, value in MODE_VALUES.items()}


def get_stroke(stroke):
    max_stroke_length = c_wrap.get_stroke_max_length()
    stroke_length = len(stroke)

    c_stroke = np.vstack((stroke, np.zeros((max_stroke_length -
                                            stroke_length, 3))))

    errors = c_wrap.get_letter(c_stroke, stroke_length)
    print errors


class MigrationStateMachine(object):
    def __init__(self, knowledge, mode, known=None):
        super(MigrationStateMachine, self).__init__()

        self.knowledge = knowledge
        self.mode = mode
        self.set_accessible_sequences(known)

        self.imu = IMU(self.knowledge['magnet_boundaries'])
        self.sp = SequenceProcessor(self.knowledge['sequences'])
        self.splitter = PipeSplitter(self.knowledge['splitting'])

        self.count_down = 0

        self.state = self.knowledge['states']['calibration']

        self.next_stroke()

    def next_stroke(self):
        self.prefix = uuid1()

    def set_accessible_sequences(self, known):
        self.known = known or self.knowledge['strokes'].keys()

    def interface_callback(self, state):
        pass

    def __call__(self, sensor_data, output=OUTPUT_MAIN):
        imu_state = self.imu.calc(sensor_data)

        splitter_state = None
        strokes = None
        choice = None
        step = None
        next_state = self.state

        split_state = None

        if not imu_state['in_calibration']:

            if self.state == self.knowledge['states']['calibration']:
                next_state = self.state = self.knowledge['states']['idle']

            splitter_state = self.splitter.set_data(sensor_data['delta'],
                                                    sensor_data['gyro'],
                                                    imu_state['accel'],
                                                    imu_state['heading'])

            if (splitter_state['state'] ==
               self.knowledge['splitting']['states']['stroke_done']):
                strokes = get_stroke(splitter_state['stroke'])

                if output != OUTPUT_TEST:
                    folder = '../raw/%s/%s' % (MODE_NAMES[self.mode],
                                               self.prefix)
                    if not path.exists(folder):
                        makedirs(folder)
                    np.savetxt('%s/%s.txt' % (folder, uuid1()),
                               splitter_state['stroke'])

                if self.mode == MODE_TRAIN:
                    next_state = self.knowledge['states']['train_done']
                    self.state = self.knowledge['states']['idle']

                elif self.mode == MODE_DEMO:
                    choice = self.sp.choose_best(strokes, self.known)
                    if choice is not None:
                        next_state = (self.knowledge['states']
                                      ['demo_%s' % choice])
                    else:
                        split_state = (self.knowledge['splitting']
                                       ['states']['strange'])
                    self.state = self.knowledge['states']['idle']

                elif self.mode == MODE_RUN:
                    is_idle = self.state == self.knowledge['states']['idle']
                    step = self.sp.next_step(strokes, self.known, is_idle)
                    if (step !=
                       self.knowledge['sequences']['states']['unsupported']):
                        key = [key for key, value in
                               self.knowledge['sequences']['states'].items()
                               if value == step][0]

                        self.state = self.knowledge['states'][key]
                        next_state = self.state
                        self.count_down = self.knowledge['count_down']
                    else:
                        split_state = (self.knowledge['splitting']
                                       ['states']['unsupported'])
            else:
                split_state = splitter_state['state']

            if self.mode == MODE_RUN:
                self.count_down -= sensor_data['delta']

                if self.count_down < 0:
                    self.count_down = 0
                    self.state = self.knowledge['states']['idle']
                    next_state = self.state

        if output == OUTPUT_MAIN:
            return next_state
        elif output == OUTPUT_WIDGET:
            return (next_state, split_state)
        elif output == OUTPUT_TEST:
            return {'imu': imu_state, 'splitter': splitter_state,
                    'strokes': strokes, 'choice': choice, 'step': step,
                    'count_down': self.count_down, 'state': next_state,
                    'split_state': split_state}

            raise ValueError('Unknown ouptup mode %d' % output)