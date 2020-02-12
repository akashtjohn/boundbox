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

    @property
    def sum(self):
        return self._x + self._y + self._z

    @property
    def diff_of_x_y(self):
        return self._x - self._y

    @x.setter
    def x(self, x_value):
        if type(x_value) != int:
            raise TypeError("x value can only be an int not a {}".type(x_value))
        self._x = x_value


    @y.setter
    def y(self, y_value):
        if type(y_value) != int:
            raise TypeError("y value can only be an int not a {}".type(y_value))
        self._y = y_value

    @z.setter
    def z(self, z_value):
        if type(z_value) != int:
            raise TypeError("z value can only be an int not a {}".type(z_value))
        self._z = z_value

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
        # TODO: include sub for z
        d_square = (self._x - other.x)**2 + (self._y - other.y)**2
        return sqrt(d_square)



