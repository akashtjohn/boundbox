#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 24 Jul 24/07/21 01:11:41 2021
@author: akash
"""
# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 24 Jul 24/07/21 01:11:41 2021
@author: akash
"""

import unittest
import warnings
import os

import cv2
from pytesseract import image_to_data, Output
import requests

# TODO: rename this class name
from boundbox import BoundBox
from boundbox import Point

test_image_url = "https://www.pyimagesearch.com/wp-content/uploads/2017/06/example_01.png"


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """
        downloads the test images and files
        """

        cls.test_files = os.path.join(os.getcwd(), 'temp_test_files')
        os.makedirs(cls.test_files, exist_ok=True)

        ########################################################################################
        # download pytesseract test image #####################################################

        # test image of pytesseract
        file_type = test_image_url.split('.')[-1]
        test_image_pytesseract = os.path.join(cls.test_files, 'pytesseract_test.' + file_type)

        try:
            test_image = requests.get(test_image_url, timeout=10)
            if test_image.status_code == 200:
                with open(test_image_pytesseract, 'wb') as f:
                    f.write(test_image.content)
            else:
                warnings.warn('could not download image properly skipping pytesseract test')
                test_image_pytesseract = None

        except requests.exceptions.ConnectionError:
            warnings.warn('could not connect to the image url to download, skipping pytesseract test')
            test_image_pytesseract = None

        cls.test_image_pytesseract = test_image_pytesseract

        ############################################################################################

    def test_default_constructor(self):
        """
        testing BoundBox default constructor
        """
        p1 = Point(0, 2)
        p2 = Point(2, 2)
        p3 = Point(2, 0)
        p4 = Point(0, 0)
        box = BoundBox(p1, p2, p3, p4, 'hello world')

        self.assertEqual(box.p1.x, 0)
        self.assertEqual(box.p1.y, 2)
        self.assertEqual(box.p2.x, 2)
        self.assertEqual(box.p2.y, 2)
        self.assertEqual(box.p3.x, 2)
        self.assertEqual(box.p3.y, 0)
        self.assertEqual(box.p4.x, 0)
        self.assertEqual(box.p4.y, 0)
        self.assertEqual(box.text_value, 'hello world')

    def test_setters_and_getters(self):
        """
        testing general getters and setters in BoundBox
        """

        p1 = Point()
        p2 = Point()
        p3 = Point()
        p4 = Point()
        box = BoundBox(p1, p2, p3, p4)

        box.p1 = Point(0, 2)
        box.p2 = Point(2, 2)
        box.p3 = Point(2, 0)
        box.p4 = Point(0, 0)
        box.text_value = 'hello world'

        self.assertEqual(box.p1.x, 0)
        self.assertEqual(box.p1.y, 2)
        self.assertEqual(box.p2.x, 2)
        self.assertEqual(box.p2.y, 2)
        self.assertEqual(box.p3.x, 2)
        self.assertEqual(box.p3.y, 0)
        self.assertEqual(box.p4.x, 0)
        self.assertEqual(box.p4.y, 0)
        self.assertEqual(box.text_value, 'hello world')

    def test_from_corner_points(self):
        """
        test creation of box from two corner points
        """

        top_left = Point(0, 4)
        bottom_right = Point(3, 0)

        box = BoundBox.from_corner_points(top_left, bottom_right, 'dummy text')

        self.assertEqual(box.p1.x, 0)
        self.assertEqual(box.p1.y, 4)
        self.assertEqual(box.p2.x, 3)
        self.assertEqual(box.p2.y, 4)
        self.assertEqual(box.p3.x, 3)
        self.assertEqual(box.p3.y, 0)
        self.assertEqual(box.p4.x, 0)
        self.assertEqual(box.p4.y, 0)
        self.assertEqual(box.text_value, 'dummy text')

    def test_pytesseract_constructor(self):
        """
        test for pytesseract to bounding box class method
        """

        if not self.test_image_pytesseract:
            warnings.warn('avoided pytesseract test because configuration is not successful')
            return

        img = cv2.imread(self.test_image_pytesseract)
        data = image_to_data(img, output_type=Output.DICT)

        box_list = BoundBox.pytesseract_boxes(data)

        # remove boxes with empty string
        valid_text_boxes = [i for i in box_list if i.text_value]

        # box containing the text 'Noisyimage', it should be the first one
        noisy_image_box = valid_text_boxes[0]

        self.assertEqual(noisy_image_box.p1.x, 77)
        self.assertEqual(noisy_image_box.p1.y, 30)
        self.assertEqual(noisy_image_box.p2.x, 420)
        self.assertEqual(noisy_image_box.p2.y, 30)
        self.assertEqual(noisy_image_box.p3.x, 420)
        self.assertEqual(noisy_image_box.p3.y, 94)
        self.assertEqual(noisy_image_box.p4.x, 77)
        self.assertEqual(noisy_image_box.p4.y, 94)
        self.assertEqual(noisy_image_box.text_value, 'Noisyimage')