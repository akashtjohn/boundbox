import cv2
import numpy as np
from math import sin, cos
from Point import Point
from Line import Line
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

        self._centroid = None
        self._length = None
        self._breadth = None

    def sort_points(self):
        """
        sort the points of the box after transformations
        :return:
        """
        self._p1, self._p2, self._p3, self._p4 = self.sort_corners(self._p1, self._p2, self._p3, self._p4)

    @staticmethod
    def sort_corners(p1, p2, p3, p4):
        """
        sort the corners based on top-right, top-left, bottom-right, bottom left as p1, p2, p3 and p4
        :param p1: point 1
        :param p2: point 2
        :param p3: point 3
        :param p4: point 4
        :return: tuple of corners in sorted order
        TODO : implement a mechanism to check points are on the same line
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

        p1 = Point(x1, y1)
        p2 = Point(x2, y2)
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
        try:
            for i in range(len(data['level'])):

                if data['text'][i]:
                    (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
                    corner_1 = Point(x, y)
                    corner_2 = Point(x+w, y+h)
                    box = cls.create_box_from_corners(corner_1, corner_2, data['text'][i])

                    box_list.append(box)
        except TypeError as ee:
            if type(box_list) != dict:
                raise TypeError("the result of pytesseract should be passed as dictionary, please try "
                                "image_to_data(img, output_type=Output.DICT)")
            raise ee

        return box_list

    @classmethod
    def box_from_contour(cls, countour):
        if len(countour) != 4:
            raise IndexError('need to approximate the contour to 4 sided polygon, currently contains {} '
                             'sides'. format(len(countour)))

        points = countour.reshape(4, 2)

        return cls.box_from_array(points)

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

    @classmethod
    def from_center(cls, center_x, center_y, length, breadth, angle):
        """
        :param center_x: x coordinate of center 
        :param center_y: y coordinate of center
        :param length: length of rectangle
        :param breadth: breadth of rectangle
        :param angle: angle in radian with respect to lower x axis
        :return: 
        """

        p1 = Point(center_x - length/2, center_y - breadth/2)
        p2 = Point(center_x + length/2, center_y - breadth/2)
        p3 = Point(center_x + length/2, center_y + breadth/2)
        p4 = Point(center_x - length/2, center_y + breadth/2)

        box = cls(p1, p2, p3, p4)
        box.rotate(angle)

        return box

    @staticmethod
    def array_to_points(array):
        p1 = Point(array[0][0], array[0][1])
        p2 = Point(array[1][0], array[1][1])
    
        p3 = Point(array[2][0], array[2][1])
        p4 = Point(array[3][0], array[3][1])

        return p1, p2, p3, p4

    def rotate(self, angle, anti_clock_wise=False):
        """
        rotates the current box the given degree in radian in anticlockwise direction
        mechanism refer to this link :
         https://math.stackexchange.com/questions/1917449/rotate-polygon-around-center-and-get-the-coordinates
        :param angle: angle in radian
        :param anti_clock_wise: if set to true rotate it clockwise
        :return:
        """

        if anti_clock_wise:
            angle *= -1
            
        coordinates = self.np_array.transpose()

        centroid = self.centroid

        centroid_matrix_raw = np.array([[centroid.x, centroid.y]]*4).transpose()
        centroid_matrix = centroid_matrix_raw.reshape(2, 4)

        rotation = np.array([
            [cos(angle), -sin(angle)],
            [sin(angle), cos(angle)]
        ])

        new_coordinates = rotation.dot(coordinates - centroid_matrix) + centroid_matrix

        interger_new_coodinates = np.around(new_coordinates.transpose())
        self._p1, self._p2, self._p3, self._p4 = self.array_to_points(interger_new_coodinates)

        self.sort_points()

    def perspective_wrap(self, img):

        width_1 = self._p3 - self._p4
        width_2 = self._p2 - self._p1

        height_1 = self._p3 - self._p2
        height_2 = self._p4 - self._p1

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
        rect[0] = [self._p1.x, self._p1.y]
        rect[1] = [self._p2.x, self._p2.y]
        rect[2] = [self._p3.x, self._p3.y]
        rect[3] = [self._p4.x, self._p4.y]

        m = cv2.getPerspectiveTransform(rect, dst)
        warp = cv2.warpPerspective(img, m, (max_width, max_height))

        return warp

    def change_ratio(self, ratio_w, ratio_h):

        self._p1.x = int(self._p1.x * ratio_w)
        self._p2.x = int(self._p2.x * ratio_w)
        self._p3.x = int(self._p3.x * ratio_w)
        self._p4.x = int(self._p4.x * ratio_w)

        self._p1.y = int(self._p1.y * ratio_h)
        self._p2.y = int(self._p2.y * ratio_h)
        self._p3.y = int(self._p3.y * ratio_h)
        self._p4.y = int(self._p4.y * ratio_h)

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
        points = np.array([[self._p1.x, self._p1.y], [self._p2.x, self._p2.y], [self._p3.x, self._p3.y],
                           [self._p4.x, self._p4.y]])
        cv2.polylines(img, np.int32([points]), True, (0, 255, 0), thickness=1)
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

    @p1.setter
    def p1(self, p):
        if isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p1 = p

    @p2.setter
    def p2(self, p):
        if isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p2 = p

    @p3.setter
    def p3(self, p):
        if isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p3 = p

    @p4.setter
    def p4(self, p):
        if isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p4 = p

    @property
    def text_value(self):
        return self._text_value

    @property
    def np_array(self):
        box = np.zeros((4, 2), dtype="int32")
        box[0] = [self._p1.x, self._p1.y]
        box[1] = [self._p2.x, self._p2.y]
        box[2] = [self._p3.x, self._p3.y]
        box[3] = [self._p4.x, self._p4.y]

        return box

    @property
    def centroid(self):
        """
        refer to https://math.stackexchange.com/questions/2484814/how-can-i-construct-the-centroid-of-a-quadrilateral
        :return:
        """

        # triangles formed by diagonal p1, p3
        # triangle 1 is p1, p2, p3
        triangle_1_x = (self._p1.x + self._p2.x + self._p3.x)/3
        triangle_1_y = (self._p1.y + self._p2.y + self._p3.y)/3

        triangle_1_c = Point(triangle_1_x, triangle_1_y)

        # triangle 2 is p1, p4, p3
        triangle_2_x = (self._p1.x + self._p4.x + self._p3.x)/3
        triangle_2_y = (self._p1.y + self._p4.y + self._p3.y)/3

        triangle_2_c = Point(triangle_2_x, triangle_2_y)

        # create line joining the centroids of triangles 3 and 4
        line_t1c_t2c = Line(triangle_1_c, triangle_2_c)

        # triangles formed by diagonal p2, p4
        # triangle 3 is p1, p2, p4
        triangle_3_x = (self._p1.x + self._p2.x + self._p4.x)/3
        triangle_3_y = (self._p1.y + self._p2.y + self._p4.y)/3

        triangle_3_c = Point(triangle_3_x, triangle_3_y)

        # triangle 4 is p2, p3, p4
        triangle_4_x = (self._p2.x + self._p4.x + self._p3.x)/3
        triangle_4_y = (self._p2.y + self._p4.y + self._p3.y)/3

        triangle_4_c = Point(triangle_4_x, triangle_4_y)

        # create line joining the centroids of triangles 3 and 4
        line_t3c_t4c = Line(triangle_3_c, triangle_4_c)

        line_intersection = line_t1c_t2c * line_t3c_t4c

        return line_intersection

    @property
    def length(self):
        length = self._p1 - self._p2
        return length

    @property
    def breadth(self):
        breadth = self._p1 - self._p4
        return breadth
