#! /usr/bin/env python2.7
# -*- coding: utf8 -*-

import unittest

import unify_definition as ud
import c_wrap
import numpy as np
import json

EPSILON = 0.00001


def almoste_equal(a, b):
    return a == b == 0 or abs(1 - a / b) < EPSILON


STROKE_PATH = ('../train/1ae92ed9-e850-11e5-8105-ac87a30aa589/' +
               '1ed90bfa-e850-11e5-a5ec-ac87a30aa589.txt')

DICT_PATH = 'migration_to_c.json'


class CheckUnifyDefinition(unittest.TestCase):

    def test_unify_stroke(self):

        segmentation = c_wrap.get_segmentation()
        max_stroke_length = c_wrap.get_stroke_max_length()

        stroke = np.loadtxt(STROKE_PATH)

        stroke_length = stroke.shape[0]

        assert stroke_length < max_stroke_length

        np_data = ud.unify_stroke(stroke, segmentation)

        c_stroke = np.vstack((stroke, np.zeros((max_stroke_length -
                                                stroke_length, 3))))

        c_data = c_wrap.unify_stroke(np.copy(c_stroke).tolist(), stroke_length)

        c_data = np.array(c_data)

        diff = np.linalg.norm(c_data - np_data)

        assert diff < EPSILON

    def test_check_stroke(self):

        segmentation = c_wrap.get_segmentation()

        stroke = np.loadtxt(STROKE_PATH)

        with open(DICT_PATH, 'r') as f:
            dictionary = json.load(f)

        description = dictionary['letters']['e5de21f0']

        assert segmentation == dictionary['segmentation']

        stroke = ud.unify_stroke(stroke, segmentation).tolist()

        assert almoste_equal(c_wrap.check_stroke(stroke, description),
                             ud.check_stroke(stroke, description))


if __name__ == '__main__':
    unittest.main()
