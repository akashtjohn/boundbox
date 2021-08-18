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
import numpy as np
#
# contour_array = np.array([[[429, 48]], [[113, 96]], [[129, 415]], [[430, 423]]])
# box = BoundBox.box_from_contour(contour_array)
# box.plot_box()

array = [[429, 48], [113, 96], [129, 415], [430, 423]]

box = BoundBox.box_from_array(array)

print("done")