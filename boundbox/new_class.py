#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:30:24 2021
@author: akash
"""

from Point_class import Point


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

        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4

        self._text_value = text_value

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
