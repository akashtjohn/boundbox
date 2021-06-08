import cv2
import numpy as np
from math import sin, cos, atan, degrees
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

from .Point_class import Point
from .Line_class import Line
from .BoundBox_utils import min_value, max_value
from .Exceptions import CannotCropImage


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
            -          p4                                  p2
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

    def __init__(self, p1, p2, p3, p4, text_value=''):

        self._p1, self._p2, self._p3, self._p4 = self.sort_corners(p1, p2, p3, p4)
        self._text_value = text_value

        # self._centroid = None
        # self._length = None
        # self._breadth = None

    def to_dict(self):
        return {'p1': self._p1, 'p2': self._p2, 'p3': self._p3, 'p4': self._p4, 'text': self.text_value}

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
        """

        # TODO : implement a mechanism to check points are on the same line
        # TODO : need to test multiple page ocr

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

        p1 = Point(int(top_left[0]), int(top_left[1]))
        p2 = Point(int(top_right[0]), int(top_right[1]))

        p3 = Point(int(bottom_right[0]), int(bottom_right[1]))
        p4 = Point(int(bottom_left[0]), int(bottom_left[1]))

        return p1, p2, p3, p4

    def __str__(self):
        # return "_p1: {},     _p2: {},     _p3: {}, " \
        #        "    _p4 {}".format(self._p1, self._p2, self._p3, self._p4)
        return "{}".format(self._text_value)

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

        if self._text_value and other.text_value:
            new_text = self._text_value + ' ' + other.text_value

        else:
            new_text = self._text_value + other.text_value

        merged_box = BoundBox(p1, p2, p3, p4, new_text.strip())
        return merged_box

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

                #if data['text'][i]:
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
    def google_ocr_boxes(cls, data):
        """
        create a list of list of boxes from results from google ocr data
        here the result is a list of list because multiple pages can be parsed together
        and a list of boxes is created for each page
        :param data: google ocr response data as dict
        :return: list(list(boxes))
        """

        page_list = []
        google_response = data['responses']

        # fill zero values for places where google ocr omitted values
        for page in google_response:
            if 'textAnnotations' not in page:
                continue
            for annotation in page['textAnnotations']:
                for vertex in range(len(annotation['boundingPoly']['vertices'])):
                    if 'x' not in annotation['boundingPoly']['vertices'][vertex]:
                        annotation['boundingPoly']['vertices'][vertex]['x'] = 0

                    elif 'y' not in annotation['boundingPoly']['vertices'][vertex]:
                        annotation['boundingPoly']['vertices'][vertex]['y'] = 0

        for page in google_response:
            box_list = []

            if 'textAnnotations' not in page:
                page_list.append([])
                continue

            text_annotations = page['textAnnotations'][1:]

            for annotation in text_annotations:
                box = cls.create_box(annotation['boundingPoly']['vertices'][0]['x'],
                                     annotation['boundingPoly']['vertices'][0]['y'],
                                     annotation['boundingPoly']['vertices'][1]['x'],
                                     annotation['boundingPoly']['vertices'][1]['y'],
                                     annotation['boundingPoly']['vertices'][2]['x'],
                                     annotation['boundingPoly']['vertices'][2]['y'],
                                     annotation['boundingPoly']['vertices'][3]['x'],
                                     annotation['boundingPoly']['vertices'][3]['y'],
                                     annotation['description'])
                box_list.append(box)
            page_list.append(box_list)

        return page_list

    @classmethod
    def labelimg_xml_boxes(cls, xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        box_list = []

        for member in root.findall('object'):
            text = member[0].text
            corner_1 = Point(int(member[4][0].text), int(member[4][1].text))
            corner_2 = Point(int(member[4][2].text), int(member[4][3].text))
            box = cls.create_box_from_corners(corner_1, corner_2, text_value=text)
            box_list.append(box)

        return box_list

    @classmethod
    def azure_ocr_boxes(cls, data: dict, merge_line: bool = False) -> list:
        """
        converts azure ocr response json into list of boundbox objects. the result will contain
        separate list for separate pages of the response

        @param data: response json from azure ocr
        @param merge_line: keep True for result on a line in single box, else every word will be seperate box
        @return: list(list(boxes))
        """

        # TODO test sorting on rotated image

        page_list = []

        recognition_results = data['recognitionResults']

        for page_result in recognition_results:
            box_list = []
            for line in page_result['lines']:
                
                # azure ocr returns both line by line ocr and individual words, user can select type of result
                if merge_line:

                    box = cls.create_box(line['boundingBox'][0],
                                         line['boundingBox'][1],
                                         line['boundingBox'][2],
                                         line['boundingBox'][3],
                                         line['boundingBox'][4],
                                         line['boundingBox'][5],
                                         line['boundingBox'][6],
                                         line['boundingBox'][7],
                                         line['text'])
                    
                    box_list.append(box)
        
                else:
                    for word in line['words']:
                        box = cls.create_box(word['boundingBox'][0],
                                             word['boundingBox'][1],
                                             word['boundingBox'][2],
                                             word['boundingBox'][3],
                                             word['boundingBox'][4],
                                             word['boundingBox'][5],
                                             word['boundingBox'][6],
                                             word['boundingBox'][7],
                                             word['text'])

                        box_list.append(box)
        
            page_list.append(box_list)

        return page_list

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

        p1, p2, p3, p4 = cls.array_to_points(array)

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

        if angle % (2*np.pi) == 0:
            return

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

    def scale_box(self, ratio_w, ratio_h):

        self._p1.x = round(self._p1.x / ratio_w)
        self._p2.x = round(self._p2.x * ratio_w)
        self._p3.x = round(self._p3.x * ratio_w)
        self._p4.x = round(self._p4.x / ratio_w)

        self._p1.y = round(self._p1.y / ratio_h)
        self._p2.y = round(self._p2.y / ratio_h)
        self._p3.y = round(self._p3.y * ratio_h)
        self._p4.y = round(self._p4.y * ratio_h)

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
        cv2.polylines(img, np.int32([points]), True, (0, 255, 0), thickness=3)
        cv2.putText(img, self.text_value, (self.p1.x, self.p1.y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 0, 255), 1)

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
        if not isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p2 = p

    @p3.setter
    def p3(self, p):
        if not isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p3 = p

    @p4.setter
    def p4(self, p):
        if not isinstance(p, Point):
            raise TypeError("point should be an instance of Point Class")
        self._p4 = p

    @property
    def text_value(self):
        return self._text_value

    @text_value.setter
    def text_value(self, value):
        if not isinstance(value, str):
            raise TypeError("text value should be an instance of str Class")
        self._text_value = value

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

    @property
    def angle(self):
        """
        we find the angle at the point p3 and the line p2, p3 with respect to x axis

         (y axis)
            -
            -
            -
    ----------------------------------------------------------------------  (x axis)
            -
            -                    p1
            -                -       -
            -            -               -
            -        p4                      -
            -            -                       -
            -                -                       p2
            -                    -               -
            -                 angle  -       -
                    ------------------- p3
            -
            -
            -
            -

        TODO : change the angle functionality to the line class
        we are finding the angle for lower line because for text bound boxes the line below the charaters will
        be always straight while the upper part might vary due to the height difference between upper case
        and lower case letters
        :return: angle in radian
        """

        dy = self.p3.y - self.p4.y
        dx = self.p3.x - self.p4.x
        angle = atan(dy/dx)

        return angle

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

    @staticmethod
    def horizontal_merge(box_1, box_2):
        """
        merge two boxes. the resulting box will have the left corners of box_1 and
        right corners of box_2
        :param box_1:
        :param box_2:
        :return:
        """

        p1 = box_1.p1
        p2 = box_2.p2
        p3 = box_2.p3
        p4 = box_1.p4

        new_text = box_1.text_value + ' ' + box_2.text_value

        try:
            merged_box = BoundBox(p1, p2, p3, p4, new_text.strip())
        except TypeError as err:
            if not box_1.p1.x or not box_1.p4.x:
                return box_2
            elif not box_2.p2.x or not box_2.p3.x:
                return box_1
            else:
                raise err

        return merged_box

    @staticmethod
    def compare_box_horizontally(box1, box2, dx):
        """
        compare the boxes to check whether box2 is on the right side of box1 and they are close
            enough and parallel
        :param box1: left side box
        :param box2: right side box
        :param dx: ratio of distance between boxes to the height of text box
        :return: True or False whether they belong in the same line
        # TODO : In the current implementation the checking of y axis is not proper for slopes. need to change it
        """

        # check the distance between box1.p3 - box2.p4 and box1.p2 - box2.p1 are almost equal

        distance_threshold = abs(box1.p2 - box2.p3) / 10

        d1 = box1.p3 - box2.p4
        d2 = box1.p2 - box2.p1
        if abs(d1 - d2) > distance_threshold:
            return False

        # check difference between angles in degree
        angle_diff_threshold = 5
        angle_diff = abs(degrees(box1.angle) - degrees(box2.angle))
        if angle_diff > angle_diff_threshold:
            return False

        box_height = box1.p2 - box1.p3
        # check they lie on the same x axis. We look for difference in y axis
        dy = box_height / 3
        if abs(box1.p3.y - box2.p4.y) > dy:
            return False

        # check distance between boxes
        distance_threshold = box_height * dx
        if box1.p2.x < box2.p1.x:
            distance_between_boxes = ((box2.p4.x - box1.p3.x) + (box2.p1.x - box1.p2.x)) / 2
            if distance_between_boxes > distance_threshold:
                return False

        elif box1.p1.x > box2.p2.x:
            return False

        return True

    @staticmethod
    def merge_box(box_list, dx=1):
        """
        This function is used to merge similar kind of text in an image and create meaningful sentences
        :param box_list: list of box objects that need to be merged
        :param dx: ratio of distance between boxes to the height of text box, keep 1 as default
        :return: list of box objects where certain boxes are merged
        # TODO : The below implementation is not optimal or the best. Need to change it to clustering
        """

        # sort the boxlist by the the x value of point p1
        box_list.sort(key=lambda k: k.p1.x)

        # set same number of flags to zero
        process_flag = [False]*len(box_list)
        results = []

        while True:
            # if all boxes are processed stop the loop
            if all(process_flag):
                break

            # take the first unprocessed box as current box and set its flag as True
            current_box_index = process_flag.index(False)
            current_box = box_list[current_box_index]
            process_flag[current_box_index] = True

            # loop through the the unprocessed boxes
            for index, b in enumerate(box_list):

                # if it is already done skip it
                if process_flag[index]:
                    continue

                # compare the box 'b' horizontally with current box and check if they are near by
                if BoundBox.compare_box_horizontally(current_box, b, dx):
                    current_box = BoundBox.horizontal_merge(current_box, b)
                    process_flag[index] = True

            results.append(current_box)

        results.sort(key=lambda k: k.p1.y)

        return results
