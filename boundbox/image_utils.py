#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on 12 Aug 12/08/21 20:30:20 2021
@author: akash

This files contains the utils for handling images

"""

import cv2


def display(img, keep_size=False):
    """
    display image, while development
    @param img: image object
    @param keep_size: keep original size of image, if this is false the image will be resized to 500x500
    """

    if not keep_size:
        img = cv2.resize(img, (500, 500))
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()