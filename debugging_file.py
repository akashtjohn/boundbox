#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 12 Aug 12/08/21 20:30:03 2021
@author: akash
"""


from boundbox import BoundBox, Point
import cv2
import json
import os
from boundbox.image_utils import display


google_ocr_good_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests',
                                    'test_samples', 'google_ocr', 'skewed_image.json')

with open(google_ocr_good_file, 'rb') as sample_response:
    response_json = json.load(sample_response)

box_list = BoundBox.google_ocr_boxes(response_json)

background = cv2.imread("/home/wasp/Downloads/rotated.png")


for box in box_list[0]:

    background = box.draw_box(background, annotate_points=True)

display(background, keep_size=True)

print('asdf')