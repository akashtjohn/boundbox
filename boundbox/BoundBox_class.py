#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:30:24 2021
@author: akash
"""

import cv2
import numpy as np

from .Point_class import Point


class BoundBox:
    """

         (y axis)
            -
            -
            -
    ----------------------------------------------------------------------  (x axis)
            -
            -                    p1
            -                  .       .
            -                .               .
            -              .                      .
            -            .                             .
            -          p4           text_value             p2
            -                .                            .
            -                     .                     .
            -                          .              .
            -                               .       .
            -                                    p3
            -
            -
            -
            -

    """

    def __init__(self, p1: Point, p2: Point, p3: Point, p4: Point, text_value: str = ''):
        """
        default constructor for BoundBox class,
        This method should only be used when the order of the points are previously known
        If there is confusion about the order of the points, use the sort and create constructor
        Avoid using this constructor unless you know exactly what you are doing, use alternate class methods instead
        # TODO: implement sort and create and replace the comment
        @param p1: top left point
        @param p2: top right point
        @param p3: bottom right point
        @param p4: bottom left point
        @param text_value: text value stored in the box
        """

        # mandatory parameters
        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4

        self._text_value = text_value

        # additional properties for optimized_calculations, optional

        # flag to denote the box edges are parallel to the coordinate axis x,y
        self._parallel_axis = False

        # flag to denote the box is a rectangle, a bounding box could easily be a rhombus and this flag will be False
        self._rectangle = False

    def __str__(self):
        """string overload"""
        return "{}".format(self._text_value)

    def __repr__(self):
        """representation overload"""
        return "{}".format(self._text_value)

    @classmethod
    def from_corner_points(cls, top_left: Point, bottom_right: Point, text_value=''):
        """
        This constructor assumes that the box is a rectangle with edges parallel to coordinate axis
        Should only be used in this case

          top_left  #########################
                    #                       #
                    #                       #
                    #                       #
                    #########################  bottom_right

        @param top_left: top left corner point, Point object
        @param bottom_right: bottonm right corner point, Point object
        @param text_value: text_value inside the box
        @return: box object
        """

        p1 = top_left
        p3 = bottom_right
        p2 = Point(bottom_right.x, top_left.y)
        p4 = Point(top_left.x, bottom_right.y)

        return BoundBox(p1, p2, p3, p4, text_value)

    @classmethod
    def pytesseract_boxes(cls, data):
        """
        Alternate constructor to create BoundBox objects from pytessearct data
        pytesseract data can be extracted using the following code

        data = image_to_data(img, output_type=Output.DICT)

        creates a list of boxes from pytesseract data
        :param data: result of pytesseract image_to_data
        :return: list of BoundBox object
        """

        box_list = []
        try:
            for i in range(len(data['level'])):

                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                corner_1 = Point(x, y)
                corner_2 = Point(x+w, y+h)
                box = cls.from_corner_points(corner_1, corner_2, data['text'][i])

                # set additional parameters for optimized calculations
                box._rectangle = True
                box._parallel_axis = True

                box_list.append(box)

        except TypeError as err:
            if type(box_list) != dict:
                raise TypeError("the result of pytesseract should be passed as dictionary, please try "
                                "image_to_data(img, output_type=Output.DICT)")
            raise err

        return box_list

    @classmethod
    def google_ocr_boxes(cls, data: dict):
        """
        Alternate constructor to create BoundBox objects google vision ocr response data
        ocr details can be found at https://cloud.google.com/vision/docs/ocr

        google ocr data returns results for multiple pages,
        so this method will return a list of lists,
        each nested list contains results of individual page

        :param data: google ocr response dictionary
        :return: list of BoundBox object
        """

        page_list = []
        google_response = data['responses']

        for page in google_response:
            box_list = []

            try:
                text_annotations = page['textAnnotations'][1:]
            except KeyError:
                # in case testAnnotation is not there, append empty list for the page
                page_list.append([])
                continue

            for annotation in text_annotations:
                # here .get operation is used with default value 0 to
                # fill zero values for places where google ocr omitted values

                p1 = Point(annotation['boundingPoly']['vertices'][0].get('x', 0),
                           annotation['boundingPoly']['vertices'][0].get('y', 0))

                p2 = Point(annotation['boundingPoly']['vertices'][1].get('x', 0),
                           annotation['boundingPoly']['vertices'][1].get('y', 0))

                p3 = Point(annotation['boundingPoly']['vertices'][2].get('x', 0),
                           annotation['boundingPoly']['vertices'][2].get('y', 0))

                p4 = Point(annotation['boundingPoly']['vertices'][3].get('x', 0),
                           annotation['boundingPoly']['vertices'][3].get('y', 0))

                box = cls(p1, p2, p3, p4, annotation['description'])
                box_list.append(box)

            page_list.append(box_list)

        return page_list

    def draw_box(self, img, write_text=True, mark_coordinates=False, annotate_points=False):
        """

        draw the box on the image

        @param img: image object, numpy array
        @param write_text: write ocr text on top of image flag, by default true
        @param mark_coordinates: write x and y coordinates on the corners of the box, by default false
        @param annotate_points: write point names such as p1, p2 etc on the corners of the box, by default false
        @return: image obj
        """
        points = np.array([[self._p1.x, self._p1.y], [self._p2.x, self._p2.y], [self._p3.x, self._p3.y],
                           [self._p4.x, self._p4.y]])
        cv2.polylines(img, np.int32([points]), True, (0, 255, 0), thickness=2)

        if write_text:
            cv2.putText(img, self.text_value, (self.p1.x, self.p1.y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 0, 255), 1)

        if mark_coordinates:
            cv2.putText(img, f"p1 ({self.p1.x}, {self.p1.y})", (self.p1.x-20, self.p1.y-5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            cv2.putText(img, f"p2 ({self.p2.x}, {self.p2.y})", (self.p2.x+5, self.p2.y-5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            cv2.putText(img, f"p3 ({self.p3.x}, {self.p3.y})", (self.p3.x+5, self.p3.y+10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            cv2.putText(img, f"p4 ({self.p4.x}, {self.p4.y})", (self.p4.x-20, self.p4.y+10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)

        if annotate_points:
            cv2.putText(img, f"p1", (self.p1.x-10, self.p1.y-5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            cv2.putText(img, f"p2", (self.p2.x+5, self.p2.y-5), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            cv2.putText(img, f"p3", (self.p3.x+5, self.p3.y+10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)
            cv2.putText(img, f"p4", (self.p4.x-10, self.p4.y+10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 0, 0), 1)

        return img

    @property
    def p1(self):
        """
        getter for top left point P1
        @return: Point object
        """
        return self._p1

    @property
    def p2(self):
        """
        getter for top right point P2
        @return: Point object
        """
        return self._p2

    @property
    def p3(self):
        """
        getter for bottom right point P3
        @return: Point object
        """
        return self._p3

    @property
    def p4(self):
        """
        getter for bottom left point P4
        @return: Point object
        """
        return self._p4

    @property
    def text_value(self):
        """
        getter for text value inside a BoundBox
        @return: Point object
        """
        return self._text_value

    @p1.setter
    def p1(self, p: Point):
        """
        setter for top left point p1
        @param p: Point object p1
        """
        self._p1 = p

    @p2.setter
    def p2(self, p: Point):
        """
        setter for top right point p2
        @param p: Point object p2
        """
        self._p2 = p

    @p3.setter
    def p3(self, p: Point):
        """
        setter for bottom right point p3
        @param p: Point object p3
        """
        self._p3 = p

    @p4.setter
    def p4(self, p: Point):
        """
        setter for top left point p4
        @param p: Point object p4
        """
        self._p4 = p

    @text_value.setter
    def text_value(self, value: str):
        """
        setter for text value inside the bounding box
        @param value: string value
        """
        self._text_value = value

