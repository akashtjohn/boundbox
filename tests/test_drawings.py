from boundbox import BoundBox
import os
import requests
import cv2
from pytesseract import image_to_data, Output

def display(img, keep_size=False):
    if not keep_size:
        img = cv2.resize(img, (500, 500))
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_drawing():

    test_image_url = "https://www.pyimagesearch.com/wp-content/uploads/2017/06/example_01.png"

    test_files = os.path.join(os.getcwd(), 'test_files')
    os.makedirs(test_files, exist_ok=True)

    # test image of pytesseract
    file_type = test_image_url.split('.')[-1]
    test_image_pytesseract = os.path.join(test_files, 'pytesseract_test.' + file_type)

    try:
        test_image = requests.get(test_image_url, timeout=10)
        if test_image.status_code == 200:
            with open(test_image_pytesseract, 'wb') as f:
                f.write(test_image.content)
        else:
            raise Exception('could not download image properly skipping pytesseract test')


    except requests.exceptions.ConnectionError:
        raise Exception('could not connect to the image url to download, skipping pytesseract test')

    img = cv2.imread(test_image_pytesseract)
    data = image_to_data(img, output_type=Output.DICT)

    box_list = BoundBox.pytesseract_boxes(data)

    for box in box_list:
        box.draw_box(img)

    display(img)


