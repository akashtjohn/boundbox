#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 24 01:30:24 2021
@author: akash
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt

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

    @staticmethod
    def sort_corners(p1, p2, p3, p4):
        """
        sort the corners based on top-right, top-left, bottom-right, bottom left as p1, p2, p3 and p4
        :param p1: point 1
        :param p2: point 2
        :param p3: point 3
        :param p4: point 4
        :return: points in sorted order
        """

        # TODO : implement a mechanism to check points are on the same line

        box = np.zeros((4, 2), dtype="int32")
        box[0] = [p1.x, p1.y]
        box[1] = [p2.x, p2.y]
        box[2] = [p3.x, p3.y]
        box[3] = [p4.x, p4.y]

        p_sum = box.sum(axis=1)
        p_diff = np.diff(box, axis=1)

        # points with max sum is bottom right and least sum is top left
        min_sum = min(p_sum)
        max_sum = max(p_sum)

        min_sum_index = np.where(p_sum == min_sum)[0]
        max_sum_index = np.where(p_sum == max_sum)[0]

        # points with least sum is top left
        if len(min_sum_index) > 1:
            # if more than one value with the same min sum exists we take the one with minimum y - x

            top_left_index = min_sum_index[0] if p_diff[min_sum_index[0]] < p_diff[min_sum_index[1]] \
                else min_sum_index[1]

        else:
            top_left_index = min_sum_index[0]

        if len(max_sum_index) > 1:
            # if more than one value with the same max sum exists we take the one with maximum y - x bottom right
            bottom_right_index = max_sum_index[0] if p_diff[max_sum_index[0]] > p_diff[max_sum_index[1]] \
                else max_sum_index[1]
        else:
            bottom_right_index = max_sum_index[0]

        top_left = box[top_left_index]
        bottom_right = box[bottom_right_index]

        remaining_box = np.delete(box, [top_left_index, bottom_right_index], axis=0)

        p_diff = np.diff(remaining_box, axis=1)

        # "y-x" is largest for bottom left and lowest for top right
        min_diff = min(p_diff)

        top_right_index = np.where(p_diff == min_diff)[0][0]
        # is one is top right the remaining one is top left
        bottom_left_index = 1 - top_right_index

        top_right = remaining_box[top_right_index]
        bottom_left = remaining_box[bottom_left_index]

        new_p1 = Point(top_left[0], top_left[1])
        new_p2 = Point(top_right[0], top_right[1])

        new_p3 = Point(bottom_right[0], bottom_right[1])
        new_p4 = Point(bottom_left[0], bottom_left[1])

        return new_p1, new_p2, new_p3, new_p4

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

    @classmethod
    def azure_read_boxes(cls, data: dict, merge_line: bool = False) -> list:
        """
        converts azure read/analyze response json into list of boundbox objects.

        This method parse the response from https://centraluseuap.dev.cognitive.microsoft.com/docs/services/computer-vision-v3-2/operations/5d986960601faab4bf452005

        note: there are multiple azure ocr services, make sure you are using the correct one

        the result will contain separate list for separate pages of the response
        @param data: response json from azure ocr
        @param merge_line: keep True for result on a line in single box, else every word will be seperate box
        @return: list(list(boxes))
        """

        page_list = []

        recognition_results = data['analyzeResult']['readResults']

        for page_result in recognition_results:
            box_list = []
            for line in page_result['lines']:

                # azure ocr returns both line by line ocr and individual words, user can select type of result
                if merge_line:

                    p1 = Point(line['boundingBox'][0], line['boundingBox'][1])
                    p2 = Point(line['boundingBox'][2], line['boundingBox'][3])
                    p3 = Point(line['boundingBox'][4], line['boundingBox'][5])
                    p4 = Point(line['boundingBox'][6], line['boundingBox'][7])

                    box = cls(p1, p2, p3, p4, line['text'])

                    box_list.append(box)

                else:
                    for word in line['words']:

                        p1 = Point(word['boundingBox'][0], word['boundingBox'][1])
                        p2 = Point(word['boundingBox'][2], word['boundingBox'][3])
                        p3 = Point(word['boundingBox'][4], word['boundingBox'][5])
                        p4 = Point(word['boundingBox'][6], word['boundingBox'][7])

                        box = cls(p1, p2, p3, p4, word['text'])

                        box_list.append(box)

            page_list.append(box_list)

        return page_list

    @classmethod
    def box_from_array(cls, array, sort_corners=False):
        """
        numpy array of points to BoundBox object
        @param : array, eg : [[429  48], [113  96], [129 415], [430 423]]
        @param : sort_corners: if the array coordinates need to be arranged to BoundBox format
        ( p1 - top left, p4 bottom right etc.), sort_corners flag can be kept as True
        """

        p1 = Point(array[0][0], array[0][1])
        p2 = Point(array[1][0], array[1][1])

        p3 = Point(array[2][0], array[2][1])
        p4 = Point(array[3][0], array[3][1])

        if sort_corners:
            p1, p2, p3, p4 = cls.sort_corners(p1, p2, p3, p4)

        return cls(p1, p2, p3, p4)

    @classmethod
    def box_from_contour(cls, contour):
        """
        converted contours with 4 points into BoundBox object
        Before passing to the function, the contour must be approximated to a 4 sided polygon
        eg. contour: [[[429  48]],, [[113  96]],, [[129 415]],, [[430 423]]]
        """

        try:
            points = contour.reshape(4, 2)
        except ValueError:
            raise IndexError('need to approximate the contour to 4 sided polygon, currently contains {} ' 
                             'sides'. format(len(contour)))

        return cls.box_from_array(points, sort_corners=True)

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
            cv2.putText(img, self.text_value, (self.p1.x+20, self.p1.y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
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

    def plot_box(self):

        np_array = self.np_array
        array = np_array.tolist()
        # repeat the first point to create a 'closed loop'
        array.append(array[0])

        # create lists of x and y values
        xs, ys = zip(*array)

        fig = plt.figure()
        ax = fig.add_subplot(111)

        # start y axis from top
        plt.gca().invert_yaxis()

        # change marking of x axis to top
        ax.xaxis.tick_top()

        for i, p in enumerate(['p1', 'p2', 'p3', 'p4']):
            ax.annotate(p, (xs[i], ys[i]))

        plt.plot(xs, ys)
        plt.grid()
        plt.show()

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

    @property
    def np_array(self):
        box = np.zeros((4, 2), dtype="int32")
        box[0] = [self._p1.x, self._p1.y]
        box[1] = [self._p2.x, self._p2.y]
        box[2] = [self._p3.x, self._p3.y]
        box[3] = [self._p4.x, self._p4.y]

        return box
