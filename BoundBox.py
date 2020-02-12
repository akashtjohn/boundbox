import cv2
import numpy as np
from Point import Point
from BoundBox_utils import min_value, max_value
from Exceptions import CannotCropImage


class BoundBox:
    """

    _p1                       _p2
       ######################
       #                    #
       #                    #
       #                    #
       #                    #
       ######################
    _p4                       _p3

    """

    def __init__(self, p1, p2, p3, p4, text_value=''):

        self._p1, self._p2, self._p3, self._p4 = self.sort_corners(p1, p2, p3, p4)
        self._text_value = text_value

    @staticmethod
    def sort_corners(p1, p2, p3, p4):
        """
        sort the corners based on top-right, top-left, bottom-right, bottom left as p1, p2, p3 and p4
        :param p1:
        :param p2:
        :param p3:
        :param p4:
        :return: tuple of corners in sorted order
        """

        # if any of the values is null return without sorting
        # this is to avoid None comparisons in case of void boxes
        if not any((p1.x, p1.y, p2.x, p2.y, p3.x, p3.y, p4.x, p4.y)):
            return p1, p2, p3, p4

        box = np.zeros((4, 2), dtype="int32")
        box[0] = [p1.x, p1.y]
        box[1] = [p2.x, p2.y]
        box[2] = [p3.x, p3.y]
        box[3] = [p4.x, p4.y]

        p_sum = box.sum(axis=1)
        p_diff = np.diff(box, axis=1)

        # points with max sum is bottom right and least sum is top left
        top_left = box[np.argmin(p_sum)]
        bottom_right = box[np.argmax(p_sum)]

        # "x-y" is largest for top right and lowest for bottom left
        bottom_left = box[np.argmax(p_diff)]
        top_right = box[np.argmin(p_diff)]

        p1 = Point(top_left[0], top_left[1])
        p2 = Point(top_right[0], top_right[1])

        p3 = Point(bottom_right[0], bottom_right[1])
        p4 = Point(bottom_left[0], bottom_left[1])

        return p1, p2, p3, p4

    def __str__(self):
        return "_p1: {},     _p2: {},     _p3: {}, " \
               "    _p4 {}".format(self._p1, self._p2, self._p3, self._p4)

    def __repr__(self):
        return "{}".format(self._text_value)

    def __add__(self, other):

        p1_x = min_value(self._p1.x, other.p1.x)
        p1_y = min_value(self._p1.y, other.p1.y)

        p1 = Point(p1_x, p1_y)

        p2_x = max_value(self._p2.x, other.p2.x)
        p2_y = min_value(self._p2.y, other.p2.y)

        p2 = Point(p2_x, p2_y)

        p3_x = max_value(self._p3.x, other.p3.x)
        p3_y = max_value(self._p3.y, other.p3.y)

        p3 = Point(p3_x, p3_y)

        p4_x = min_value(self._p4.x, other.p4.x)
        p4_y = max_value(self._p4.y, other.p4.y)

        p4 = Point(p4_x, p4_y)

        new_text = self._text_value + ' ' + other.text_value

        return BoundBox(p1, p2, p3, p4, new_text.strip())

    @classmethod
    def create_box_from_corners(cls, corner_1, corner_2, text_value=None):
        """

          corner_1  #########################
                    #                       #
                    #                       #
                    #                       #
                    #########################  corner_2

        :param text_value: text value inside the box
        :param corner_1: point object of corner 1
        :param corner_2: point object of corner 2
        :return: box object
        """

        p1 = corner_1
        p3 = corner_2
        p2 = Point(corner_1.x, corner_2.y)
        p4 = Point(corner_2.x, corner_1.y)

        return BoundBox(p1, p2, p3, p4, text_value)

    @classmethod
    def create_box(cls, x1, y1, x2, y2, x3, y3, x4, y4, text_value=None):

        p1 = Point(x1, x2)
        p2 = Point(y1, y2)
        p3 = Point(x3, y3)
        p4 = Point(x4, y4)

        return cls(p1, p2, p3, p4, text_value)

    @classmethod
    def void_box(cls):
        return cls.create_box(None, None, None, None, None, None, None, None, '')

    @classmethod
    def pytesseract_boxes(cls, data):
        """
        creates a list of boxes from pytesseract data
        :param data: result of pytesseract image_to_data
        :return: list of BoundBox object
        """

        box_list = []

        for i in range(len(data['level'])):

            if data['text'][i]:
                (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                corner_1 = Point(x, y)
                corner_2 = Point(x+w, y+h)
                box = cls.create_box_from_corners(corner_1, corner_2, data['text'][i])

                box_list.append(box)

        return box_list

    @classmethod
    def box_from_contour(cls, countour):
        if len(countour) != 4:
            raise IndexError('need to approximate the contour to 4 sided polygon, currently contains {} '
                             'sides'. format(len(countour)))

        points = countour.reshape(4, 2)

        p1 = Point(points[0][0], points[0][1])
        p2 = Point(points[1][0], points[1][1])

        p3 = Point(points[2][0], points[2][1])
        p4 = Point(points[3][0], points[3][1])

        return cls(p1, p2, p3, p4)

    @classmethod
    def box_from_array(cls, array):
        if len(array) != 4:
            raise IndexError('need to approximate the contour to 4 sided polygon, currently contains {} '
                             'sides'. format(len(array)))

        p1 = Point(array[0][0], array[0][1])
        p2 = Point(array[1][0], array[1][1])

        p3 = Point(array[2][0], array[2][1])
        p4 = Point(array[3][0], array[3][1])

        return cls(p1, p2, p3, p4)

    def perspective_wrap(self, img):

        width_1 = self.p3 - self.p4
        width_2 = self.p2 - self.p1

        height_1 = self.p3 - self.p2
        height_2 = self.p4 - self.p1

        # take the maximum of the width and height for the new image

        max_width = max(int(width_1), int(width_2))
        max_height = max(int(height_1), int(height_2))

        # construct our destination points

        dst = np.array([
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1]], dtype="float32")

        # calculate the perspective transform matrix and warp
        # the perspective to grab the screen
        rect = np.zeros((4, 2), dtype="float32")
        rect[0] = [self.p1.x, self.p1.y]
        rect[1] = [self.p2.x, self.p2.y]
        rect[2] = [self.p3.x, self.p3.y]
        rect[3] = [self.p4.x, self.p4.y]

        m = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(img, m, (max_width, max_height))

        return warp

    def crop_image(self, img):

        ymin_value = min_value(self._p1.y, self._p2.y)
        ymax_value = max_value(self._p3.y, self._p4.y)
        xmin_value = min_value(self._p1.x, self._p4.x)
        xmax_value = max_value(self._p2.x, self._p3.x)

        if ymin_value > ymax_value or xmin_value > xmax_value:
            raise CannotCropImage('the image cannot be cropped because the edges does not create a proper rectangle')

        cropped_img = img[ymin_value:ymax_value, xmin_value:xmax_value]

        return cropped_img

    def draw_box(self, img):
        points = np.array([[self.p1.x, self.p1.y], [self.p2.x, self.p2.y], [self.p3.x, self.p3.y],
                           [self.p4.x, self.p4.y]])
        cv2.polylines(img, np.int32([points]), 1, (255, 255, 255))
        return img

    @property
    def p1(self):
        return self._p1

    @property
    def p2(self):
        return self._p2

    @property
    def p3(self):
        return self._p3

    @property
    def p4(self):
        return self._p4

    @property
    def text_value(self):
        return self._text_value

    @property
    def np_array(self):
        box = np.zeros((4, 2), dtype="int32")
        box[0] = [self.p1.x, self.p1.y]
        box[1] = [self.p2.x, self.p2.y]
        box[2] = [self.p3.x, self.p3.y]
        box[3] = [self.p4.x, self.p4.y]

        return box
