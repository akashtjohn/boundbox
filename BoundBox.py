from Point import Point
from BoundBox_utils import min_value, max_value
from Exceptions import CannotCropImage


class BoundBox2D:
    """

    p1                       p2
       ######################
       #                    #
       #                    #
       #                    #
       #                    #
       ######################
    p4                       p3

    """

    def __init__(self, p1, p2, p3, p4, text_value=None):

        self._p1 = p1
        self._p2 = p2
        self._p3 = p3
        self._p4 = p4
        self._text_value = text_value

    def __str__(self):
        return "p1: {},     p2: {},     p3: {}, " \
               "    p4 {}".format(self._p1, self._p2, self._p3, self._p4)

    def __repr__(self):
        return "{}".format(self._text_value)

    def __add__(self, other):

        p1_x = min_value(self.p1.x, other.p1.x)
        p1_y = min_value(self.p1.y, other.p1.y)

        p1 = Point(p1_x, p1_y)

        p2_x = max_value(self.p2.x, other.p2.x)
        p2_y = min_value(self.p2.y, other.p2.y)

        p2 = Point(p2_x, p2_y)

        p3_x = max_value(self.p3.x, other.p3.x)
        p3_y = max_value(self.p3.y, other.p3.y)

        p3 = Point(p3_x, p3_y)

        p4_x = min_value(self.p4.x, other.p4.x)
        p4_y = max_value(self.p4.y, other.p4.y)

        p4 = Point(p4_x, p4_y)

        new_text = self.text_value + ' ' + other.text_value

        return BoundBox2D(p1, p2, p3, p4, new_text)

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

        return BoundBox2D(p1, p2, p3, p4, text_value)

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

    def crop_image(self, img):

        ymin_value = min_value(self.p1.y, self.p2.y)
        ymax_value = max_value(self.p3.y, self.p4.y)
        xmin_value = min_value(self.p1.x, self.p4.x)
        xmax_value = max_value(self.p2.x, self.p3.x)

        if ymin_value > ymax_value or xmin_value > xmax_value:
            raise CannotCropImage('the image cannot be cropped because the edges does not create a rectangle')
        croped_img = img[ymin_value:ymax_value, xmin_value:xmax_value]

        return croped_img

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

