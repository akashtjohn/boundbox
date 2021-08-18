# boundbox

boundbox is a lightweight container for OCR bounding boxes. 



### Key Features
Bounding box operations such as scaling, merging. Developers can use boundbox when they need the flexibility
to change between different OCR services or bounding box 
* Easy switch between OCR services with minimum code change
* Supports bounding box operation such as scaling, merging, rotating etc.
* Supports most of the commonly used OCR services such as 
  pytesseract, Google Vision Ocr, Azure OCR etc.
* Support labelling tools such as LabelImg and box operations on images  
* Image transformation features such as perspective transformations and box visualizations
  

### Installation
boundbox supports Python >= 3.6. You can install it using

    pip install boundbox

### Box corners



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

## Sample



![drawn](https://user-images.githubusercontent.com/50582261/129756043-61029488-1fb2-4055-a0ac-04f1a3211ffd.png)



## Usage



### pytesseract

    from boundbox import BoundBox

    import cv2
    from pytesseract import image_to_data, Output
    
    # load image to numpy array
    img = cv2.imread('test.png')
    
    # image to pytesseract data
    data = image_to_data(img, output_type=Output.DICT)
    
    # list of all bounding boxes found in image
    box_list = BoundBox.pytesseract_boxes(data)
    
    box = box_list[0]

    # corner points of the boxes are accessed by variable 'p1', 'p2', 'p3', 'p4'

    print(box.p1.x, box.p1.y)
    print(box.p2.x, box.p2.y)
    print(box.p3.x, box.p3.y)
    print(box.p4.x, box.p4.y)

    >>> 77 30
    >>> 420 30
    >>> 420 94
    >>> 77 94

    # text value is accessed by 'text_value' 

    print(box.text_value)

    >>> Noisyimage
    
    # draw the box on the image
    drawn = box.draw_box(img)

### Google Vision OCR

Response from [google vision ocr](https://cloud.google.com/vision/docs/ocr) can be converted to **BoundBox** objects. 
Since the response might contain multiple pages, the method returns list of list, each nested list contains results 
from individual page

    # pass google ocr response dictionary to google_ocr_boxes method

    BoundBox.google_ocr_boxes(response_dict)
    
    # first box from the first page
    box = box_list[0][0]

    print(box.text_value)
    >>> Noisy


### Azure OCR

Response from [Azure Read](https://centraluseuap.dev.cognitive.microsoft.com/docs/services/computer-vision-v3-2/operations/5d986960601faab4bf452005)
can be converted to **BoundBox** objects. Since the response might contain multiple pages, the method
returns a list of list, each nested list contains results from individual page

    # pass azure read response dictionary to azure_read_boxes method

    BoundBox.azure_read_boxes(response_dict,  merge_line=False)
    
    # first box from the first page
    box = box_list[0][0]

    print(box.text_value)
    >>> Noisy

Azure read returns both line by line and word by word results.
The ***merge_line*** parameter can be used to select **line** or **word** results.
 By default ***merge_line*** is false

###### note: Azure has various OCR services, Currently boundbox supports only [Azure Read](https://centraluseuap.dev.cognitive.microsoft.com/docs/services/computer-vision-v3-2/operations/5d986960601faab4bf452005)


### Image Contour 

cv2 image [contour](https://docs.opencv.org/3.4/d4/d73/tutorial_py_contours_begin.html) can be converted to BoundBox object. For this the contour must be 
[approximated polygon](https://www.geeksforgeeks.org/python-detect-polygons-in-an-image-using-opencv/)
with 4 sided. 

            box = BoundBox.box_from_contour(contour_array)

### From 2D numpy array or list
2D numpy array or 2D list can be directly converted to BoundBox objects
    
        array = [[429, 48], [113, 96], [129, 415], [430, 423]]
        box = BoundBox.box_from_array(array, sort_corners=True)

The parameter ***sort_corners*** will rearrange the points to default BoundBox format (
p1 will be top left, p2 top right, p3 bottom right, p4 bottom left ) 

Default value for ***sort_corners*** is False. It is recommended to keep ***sort_corners = True*** 
for image operations.

###








