import pytesseract
from pytesseract import image_to_string, Output
import cv2

from BoundBox import BoundBox2D

img = cv2.imread("/home/wasp/WorkingDirectory/BoundBox/test_images/tesseract_test.png")


d = pytesseract.image_to_data(img, output_type=Output.DICT)


box_list = BoundBox2D.pytesseract_boxes(d)


k = BoundBox2D.void_box()


for i in box_list:
    k += i

bg = k.crop_image(img)

cv2.imshow('asfd', bg)
cv2.waitKey(0)
cv2.destroyAllWindows()

print('hai')

print(k.text_value)

print('finished')

















