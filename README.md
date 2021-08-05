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
boundbox supports Python >= 3.6. You can install it by doing

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


![drawn](https://user-images.githubusercontent.com/50582261/126544566-3388d37d-b98c-456c-9943-96f9140c1ba9.png)


### Google Vision OCR

Response from [google vision ocr](https://cloud.google.com/vision/docs/ocr) can be converted to boundbox objects. 
Since the response might contain multiple pages, the method returns list of list, each nested list contains results 
from individual page

    # pass google ocr response dictionary to google_ocr_boxes method

    BoundBox.google_ocr_boxes(response_dict)
    
    # first box from the first page
    box = box_list[0][0]

    print(box.text_value)
    >>> Noisy


