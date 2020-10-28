import unittest
import requests
import os
from math import radians, degrees
import numpy as np
import cv2
import warnings
import json
from pytesseract import image_to_data, Output

import sys
sys.path.insert(0, '..')

from boundbox.BoundBox_class import BoundBox
from boundbox.Point_class import Point

test_image_url = "https://www.pyimagesearch.com/wp-content/uploads/2017/06/example_01.png"

# TODO : unit tests compare box and merge box

class MyTestCase(unittest.TestCase):

    test_files = ''
    @classmethod
    def setUpClass(cls):
        """
        downloads the test image
        :return:
        """

        cls.test_files = os.path.join(os.getcwd(), 'test_files')
        os.makedirs(cls.test_files, exist_ok=True)

        # test image of pytesseract
        file_type = test_image_url.split('.')[-1]
        test_image_pytesseract = os.path.join(cls.test_files, 'pytesseract_test.'+file_type)

        try:
            test_image = requests.get(test_image_url, timeout=10)
            if test_image.status_code == 200:
                with open(test_image_pytesseract, 'wb') as f:
                    f.write(test_image.content)
            else:
                warnings.warn('could not download image properly skipping pytesseract test')
                test_image_pytesseract = None

        except requests.exceptions.ConnectionError:
            warnings.warn('could not connect to the image url to download, skipping pytesseract test')
            test_image_pytesseract = None

        cls.test_image_pytesseract = test_image_pytesseract

    @classmethod
    def tearDownClass(cls):
        """
        removes the created files for the test
        :return:
        """

        files = os.listdir(cls.test_files)
        for file in files:
            full_path = os.path.join(cls.test_files, file)
            os.remove(full_path)

        os.rmdir(cls.test_files)

    def test_addition(self):
        """
        test of + operator overloading,
        addition of two boxes to generate a new box
        :return:
        """
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

        p1 = Point(0, 0)
        p2 = Point(2, 0)
        p3 = Point(2, 2)
        p4 = Point(0, 2)
        box_4 = BoundBox(p1, p2, p3, p4)

        p4 = Point(2, 0)
        p5 = Point(6, 0)
        p6 = Point(6, 3)
        p7 = Point(2, 3)
        box_5 = BoundBox(p4, p5, p6, p7)

        box_6 = box_4 + box_5

        self.assertEqual(box_6.p1.x, 0)
        self.assertEqual(box_6.p1.y, 0)
        self.assertEqual(box_6.p2.x, 6)
        self.assertEqual(box_6.p2.y, 0)
        self.assertEqual(box_6.p3.x, 6)
        self.assertEqual(box_6.p3.y, 3)
        self.assertEqual(box_6.p4.x, 0)
        self.assertEqual(box_6.p4.y, 3)
        self.assertEqual(box_6.text_value, '')

    def test_horizontal_merge(self):
        """
        test of + operator overloading,
        addition of two boxes to generate a new box
        :return:
        """
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

        box_3 = BoundBox.horizontal_merge(box_1, box_2)

        self.assertEqual(box_3.p1.x, 0)
        self.assertEqual(box_3.p1.y, 0)
        self.assertEqual(box_3.p2.x, 6)
        self.assertEqual(box_3.p2.y, 0)
        self.assertEqual(box_3.p3.x, 6)
        self.assertEqual(box_3.p3.y, 3)
        self.assertEqual(box_3.p4.x, 0)
        self.assertEqual(box_3.p4.y, 2)
        self.assertEqual(box_3.text_value, 'hello world')

    def test_pytesseract(self):

        if not self.test_image_pytesseract:
            warnings.warn('avoided pytesseract test')
            return
        img = cv2.imread(self.test_image_pytesseract)
        data = image_to_data(img, output_type=Output.DICT)

        box_list = BoundBox.pytesseract_boxes(data)

        merged_box = BoundBox.void_box()

        for box in box_list:
            merged_box += box

        self.assertEqual(merged_box.text_value, 'Noisyimage to test Tesseract OCR')

    def test_google_ocr(self):

        google_ocr_sample_response_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       'google_ocr_sample_response.json')

        with open(google_ocr_sample_response_file, 'rb') as sample_reponse:
            reponse_json = json.load(sample_reponse)

        box_list = BoundBox.google_ocr_boxes(reponse_json)

        merged_box = BoundBox.void_box()

        # google ocr returns a list of list
        for box in box_list[0]:
            merged_box += box

        self.assertEqual(merged_box.text_value, 'WAITING? PLEASE TURN OFF YOUR ENGINE')
        
    def test_labelimg_xml(self):
        
        labelimg_xml_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                                       'labelImg_xml.xml')
        box_list = BoundBox.labelimg_xml_boxes(labelimg_xml_file)
        
        self.assertEqual(len(box_list), 2)
        
        # test values of the second box
        self.assertEqual(box_list[1].p1.x, 498)
        self.assertEqual(box_list[1].p1.y, 188)
        self.assertEqual(box_list[1].p3.x, 607)
        self.assertEqual(box_list[1].p3.y, 296)
        self.assertEqual(box_list[1].text_value, 'cube')

    def test_image_from_contour(self):
        contour_array = np.array([[[429, 48]], [[113, 96]], [[129, 415]], [[430, 423]]])
        box = BoundBox.box_from_contour(contour_array)

        self.assertEqual(box.p1.x, 113)
        self.assertEqual(box.p1.y, 96)
        self.assertEqual(box.p2.x, 429)
        self.assertEqual(box.p2.y, 48)
        self.assertEqual(box.p3.x, 430)
        self.assertEqual(box.p3.y, 423)
        self.assertEqual(box.p4.x, 129)
        self.assertEqual(box.p4.y, 415)

    def test_sorting(self):
        np_array = [[4, 2], [2, 4], [8, 6], [6, 8]]
        box = BoundBox.box_from_array(np_array)

        self.assertEqual(box.p1.x, 4)
        self.assertEqual(box.p1.y, 2)
        self.assertEqual(box.p2.x, 8)
        self.assertEqual(box.p2.y, 6)
        self.assertEqual(box.p3.x, 6)
        self.assertEqual(box.p3.y, 8)
        self.assertEqual(box.p4.x, 2)
        self.assertEqual(box.p4.y, 4)

        np_array = [[4, 2], [2, 4], [8, 6], [6, 9]]
        box = BoundBox.box_from_array(np_array)
        self.assertEqual(box.p1.x, 4)
        self.assertEqual(box.p1.y, 2)
        self.assertEqual(box.p2.x, 8)
        self.assertEqual(box.p2.y, 6)
        self.assertEqual(box.p3.x, 6)
        self.assertEqual(box.p3.y, 9)
        self.assertEqual(box.p4.x, 2)
        self.assertEqual(box.p4.y, 4)

    def test_np_array(self):
        array = [[113, 96], [429, 48], [430, 423], [129, 415]]
        box = BoundBox.box_from_array(array)

        self.assertListEqual(array, box.np_array.tolist())

    def test_length_breadth(self):

        np_array = [[4, 2], [2, 4], [8, 6], [6, 8]]
        box = BoundBox.box_from_array(np_array)
        self.assertEqual(round(box.length, 2), 5.66)
        self.assertEqual(round(box.breadth, 2), 2.83)

    def test_rotation(self):

        # simple check
        box_1 = BoundBox.box_from_array([[2, 2], [2, 4], [6, 2], [6, 4]])
        box_1.rotate(radians(90), anti_clock_wise=False)
        expected_result_1 = [[3, 1], [5, 1], [5, 5], [3, 5]]
        self.assertListEqual(box_1.np_array.tolist(), expected_result_1)

        # clock wise rotation
        box_2 = BoundBox.box_from_array([[100, 100], [200, 100], [200, 400], [100, 400]])
        box_2.rotate(radians(45), anti_clock_wise=False)
        expected_result_2 = [[221, 109], [291, 179], [79, 391], [9, 321]]
        self.assertListEqual(box_2.np_array.tolist(), expected_result_2)

        # anti clock wise rotation
        box_3 = BoundBox.box_from_array([[100, 100], [200, 100], [200, 400], [100, 400]])
        box_3.rotate(radians(45), anti_clock_wise=True)
        expected_result_3 = [[79, 109], [291, 321], [221, 391], [9, 179]]
        self.assertListEqual(box_3.np_array.tolist(), expected_result_3)

        # 360 degree rotation
        box_3 = BoundBox.box_from_array([[100, 100], [200, 100], [200, 400], [100, 400]])
        box_3.rotate(radians(360), anti_clock_wise=True)
        expected_result_3 = [[100, 100], [200, 100], [200, 400], [100, 400]]
        self.assertListEqual(box_3.np_array.tolist(), expected_result_3)

    def test_centroid(self):

        box_1 = BoundBox.box_from_array([[100, 100], [500, 100], [500, 500], [100, 500]])
        centroid_1 = box_1.centroid

        self.assertEqual(centroid_1.x, 300)
        self.assertEqual(centroid_1.y, 300)

        box_2 = BoundBox.box_from_array([[107, 95], [352, 117], [420, 615], [80, 590]])
        centroid_2 = box_2.centroid

        self.assertEqual(centroid_2.x, 240)
        self.assertEqual(centroid_2.y, 368)

        box_3 = BoundBox.box_from_array([[4, 2], [2, 4], [8, 6], [6, 9]])
        centroid_3 = box_3.centroid

        self.assertEqual(centroid_3.x, 5)
        self.assertEqual(centroid_3.y, 5)

    def test_box_from_center(self):
        center_x = 150
        center_y = 250
        length = 100
        breadth = 300
        angle = radians(45)
        box = BoundBox.from_center(center_x, center_y, length, breadth, angle)
        expected_result = [[221, 109], [291, 179], [79, 391], [9, 321]]
        self.assertListEqual(box.np_array.tolist(), expected_result)

    def test_scale_box(self):
        box = BoundBox.box_from_array([[100, 100], [200, 100], [200, 400], [100, 400]])
        box.scale_box(1.5, 2)
        expected_result = [[67, 50], [300, 50], [300, 800], [67, 800]]
        self.assertListEqual(box.np_array.tolist(), expected_result)

    def test_change_ratio(self):
        box = BoundBox.box_from_array([[100, 100], [200, 100], [200, 400], [100, 400]])
        box.change_ratio(1.5, 2)
        expected_result = [[150, 200], [300, 200], [300, 800], [150, 800]]
        self.assertListEqual(box.np_array.tolist(), expected_result)

    def test_box_angle(self):
        box1 = BoundBox.box_from_array([[10, 10], [40, 15], [30, 30], [20, 20]])
        angle1 = box1.angle
        self.assertEqual(degrees(angle1), 45)

        box2 = BoundBox.box_from_array([[100, 100], [200, 100], [200, 400], [100, 400]])
        angle2 = box2.angle
        self.assertEqual(degrees(angle2), 0)


if __name__ == '__main__':
    unittest.main()
