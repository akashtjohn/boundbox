#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 00:39:30 2021
@author: akash

This file contains the container class for a Point in three dimensional coordinate space
Even though this is a support class for 2d BoundBox class, we give support for 3D coordinates
integer or float can be an axis coordinate. float is allowed so the class can store
coordinates like latitude or longitude if needed
"""


from math import sqrt


class Point:

    """

            .(x,y,z)

    """
    def __init__(self, x=0, y=0, z=0):
        """
        @param x: x coordinate of the point, should be an integer/float, default value 0
        @param y: y coordinate of the point, should be an integer/float, default value 0
        @param z: z coordinate of the point, should be an integer/float, default value 0
        """

        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        """
        getter for x coordinate of a point in 3D coordinate space
        """
        return self._x

    @property
    def y(self):
        """
        getter for y coordinate of a point in 3D coordinate space
        """
        return self._y

    @property
    def z(self):
        """
        getter for z coordinate of a point in 3D coordinate space
        """
        return self._z

    @x.setter
    def x(self, x_value):
        """
        setter of x coordinate of a point in 3D coordinate space
        @param x_value: int/float value
        """

        self._x = x_value

    @y.setter
    def y(self, y_value):
        """
        setter of y coordinate of a point in 3D coordinate space
        @param y_value: int/float value
        """
        self._y = y_value

    @z.setter
    def z(self, z_value):
        """
        setter of z coordinate of a point in 3D coordinate space
        @param z_value: int/float value
        """
        self._z = z_value

    def __repr__(self):
        """representation for Point object"""
        # check valid z to make representation of 2d points easier to read
        if self._z:
            return "({}, {}, {})".format(self._x, self._y, self._z)
        else:
            return "({}, {})".format(self._x, self._y)

    def __str__(self):
        """string conversion for Point object"""
        # check valid z to make representation of 2d points easier to read
        if self._z:
            return "({}, {}, {})".format(self._x, self._y, self._z)
        else:
            return "({}, {})".format(self._x, self._y)

    def __sub__(self, other) -> float:
        """
        finds the Euclidean distance between two points
        :param other: second point
        :return: distance
        """
        d_square = (self._x - other.x)**2 + (self._y - other.y)**2 + (self._z - other.z)**2
        return sqrt(d_square)



