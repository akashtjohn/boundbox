import unittest
from ..src.Point_class import Point


class MyTestCase(unittest.TestCase):

    def test_point(self):

        p1 = Point(2, 3, 7)

        self.assertEqual(p1.x, 2)
        self.assertEqual(p1.y, 3)
        self.assertEqual(p1.z, 7)

    def test_distance(self):

        p1 = Point(3, 5)
        p2 = Point(7, 8)
        d = p1 - p2

        self.assertEqual(d, 5)

    def test_sum(self):

        p = Point(1, 2, 3)
        self.assertEqual(6, p.sum)

    def test_diff_of_x_y(self):

        p = Point(4, 2)
        self.assertEqual(p.diff_of_x_y, 2)


if __name__ == '__main__':
    unittest.main()
