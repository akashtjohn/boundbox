import unittest
import urllib
import os
import cv2
from pytesseract import image_to_data, Output
from BoundBox import BoundBox
from Point import Point


test_image_url = "https://www.pyimagesearch.com/wp-content/uploads/2017/06/example_01.png"


class MyTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        test_files = os.path.join(os.getcwd(), 'test_files')
        os.makedirs(test_files, exist_ok=True)

        #test image of pytesseract
        test_image_pytesseract = os.path.join(test_files, 'pytesseract_test')
        urllib.request.urlretrieve(test_image_url, test_image_pytesseract)

        cls.test_image_pytesseract = test_image_pytesseract

    def test_addition(self):

        p1 = Point(0, 0)
        p2 = Point(2, 0)
        p3 = Point(2, 2)
        p4 = Point(0, 2)
        box_1 = BoundBox(p1, p2, p3, p4, 'hello')

        p4 = Point(2, 0)
        p5 = Point(6, 0)
        p6 = Point(6, 3)
        p7 = Point(2, 3)
        box_2 = BoundBox(p4, p5, p6, p7, 'world')

        box_3 = box_1 + box_2

        self.assertEqual(box_3.p1.x, 0)
        self.assertEqual(box_3.p1.y, 0)
        self.assertEqual(box_3.p2.x, 6)
        self.assertEqual(box_3.p2.y, 0)
        self.assertEqual(box_3.p3.x, 6)
        self.assertEqual(box_3.p3.y, 3)
        self.assertEqual(box_3.p4.x, 0)
        self.assertEqual(box_3.p4.y, 3)
        self.assertEqual(box_3.text_value, 'hello world')

    def test_pytesseract(self):

        img = cv2.imread(self.test_image_pytesseract)
        data = image_to_data(img, output_type=Output.DICT)

        box_list = BoundBox.pytesseract_boxes(data)

        merged_box = BoundBox.void_box()
        for box in box_list:
            merged_box += box

        self.assertEqual(merged_box.text_value, 'Noisyimage to test Tesseract OCR')


if __name__ == '__main__':
    unittest.main()
