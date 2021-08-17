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

google_ocr_good_file = "/home/wasp/WorkingDirectory/boundbox_0.1/boundbox/tests/test_samples/azure_ocr/good_text.json"

with open(google_ocr_good_file, 'rb') as sample_response:
    response_json = json.load(sample_response)

box_list = BoundBox.azure_read_boxes(response_json, merge_line=True)
box = box_list[0][0]

# corner points of the boxes are accessed by variable 'p1', 'p2', 'p3', 'p4'

print(box.p1.x, box.p1.y)
print(box.p2.x, box.p2.y)
print(box.p3.x, box.p3.y)
print(box.p4.x, box.p4.y)

# text value is accessed by 'text_value'

print(box.text_value)
img = cv2.imread("/home/wasp/Downloads/test.png")
# draw the box on the image
drawn = box.draw_box(img, annotate_points=True)
print('asdf')
cv2.imwrite('result.png', drawn)
display(drawn, keep_size=True)