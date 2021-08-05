#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:30:24 2021
@author: akash
"""

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
