from math import sqrt


class Point:

    """

            .(x,y,z)

    """
    def __init__(self, x=0, y=0, z=0):
        self._x = x
        self._y = y
        self._z = z

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def z(self):
        return self._z

    def __repr__(self):
        if self._z:
            return "({}, {}, {})".format(self._x, self._y, self._z)
        else:
            return "({}, {})".format(self._x, self._y)

    def __str__(self):
        if self._z:
            return "({}, {}, {})".format(self._x, self._y, self._z)
        else:
            return "({}, {})".format(self._x, self._y)


    def __sub__(self, other):
        """
        finds the Euclidean distance between two points
        :param other:
        :return: distance
        """
        d_square = (self.x - other.x)**2 + (self.y - other.y)**2
        return sqrt(d_square)

