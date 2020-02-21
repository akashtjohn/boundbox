import numpy as np
from Point import Point


class Line:

    def __init__(self, p1, p2):
        """
            p1 -------------------------- p2

        """
        self._p1 = p1
        self._p2 = p2

    @property
    def np_array(self):
        array = np.array([[self._p1.x, self._p1.y], [self._p2.x, self._p2.y]])
        return array

    def __mul__(self, other):
        """
        overloaded the multiplication operator to find the intersection point of two lines
        refer to https://stackoverflow.com/questions/20677795/how-do-i-compute-the-intersection-point-of-two-lines
        :param other:
        :return: the point where the line_s meet
        """
        line_1 = self.np_array
        line_2 = other.np_array
        
        x_diff = [line_1[0][0] - line_1[1][0], line_2[0][0] - line_2[1][0]]

        y_diff = [line_1[0][1] - line_1[1][1], line_2[0][1] - line_2[1][1]]

        diff_matrix = np.array([x_diff, y_diff])

        det = np.linalg.det(diff_matrix)

        if det == 0:
            raise ValueError('lines does not intersect')

        d = [np.linalg.det(line_1), np.linalg.det(line_2)]

        x_diff = (line_1[0][0] - line_1[1][0], line_2[0][0] - line_2[1][0])
        y_diff = (line_1[0][1] - line_1[1][1], line_2[0][1] - line_2[1][1])

        x = round(np.linalg.det(np.array([d, x_diff])) / det)
        y = round(np.linalg.det(np.array([d, y_diff])) / det)

        return Point(x, y)
