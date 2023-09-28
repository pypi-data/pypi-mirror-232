"""The api for ez_img_diff, contains a single function

Functions
-------
compare_images
    Uses SSIM to compare two images and generate a diff image and similarity score
    
Example
-------
### Compare 2 images without saving difference files
```python
from ez_img_diff.api import compare_images

img1 = "baseline.png"
img2 = "current.png"

compare_images(im1, img2) # 14.03
```

### Compare 2 images with saving difference and threshold files
```python
from ez_img_diff.api import compare_images

img1 = "baseline.png"
img2 = "current.png"

compare_images(im1, img2, "difference.png", "threshold.png") # 14.03
```
"""

# Standard lib dependencies
import os
from typing import Dict, Union                     # Allows for type hinting

# Third party Dependencies
import cv2                                         # Computer vision library
import imutils                                     # Utilities for cv2 objects
from skimage.metrics import structural_similarity  # Used to compare images

def compare_images(image_1:str, image_2:str, diff_file_path:Union[str,None]=None, thresh_file_path:Union[str,None]=None) -> float:
    """Uses SSIM to compare two images and generate a diff image and similarity score

    Parameters
    ----------
    image_1 : str
        The first image to compare

    image_2 : str
        The second image to compare

    diff_file_path : str
        The path to store the difference image to (default: None)

    thresh_file_path : str
        The path to store the threshold image to (default: None)

    References
    ----------
    - https://www.imatest.com/support/docs/23-1/ssim/#:~:text=Introduction%20%E2%80%94%20The%20Structural%20Similarity%20Index,by%20losses%20in%20data%20transmission.
    - https://en.wikipedia.org/wiki/Structural_similarity
    - https://medium.com/srm-mic/all-about-structural-similarity-index-ssim-theory-code-in-pytorch-6551b455541e

    Raises
    ------
    FileNotFoundError:
        When either image does not exist
    
    Returns
    -------
    float
        The difference (as a whole percentage) between two images to 3 decimal places i.e. 0.33 or 13.54
        
    Example
    -------
    ### Compare 2 images without saving difference files
    ```python
    from ez_img_diff.api import compare_images
    
    img1 = "baseline.png"
    img2 = "current.png"
    
    compare_images(im1, img2) # 14.03
    ```

    ### Compare 2 images with saving difference and threshold files
    ```python
    from ez_img_diff.api import compare_images
    
    img1 = "baseline.png"
    img2 = "current.png"
    
    compare_images(im1, img2, "difference.png", "threshold.png") # 14.03
    ```
    """
    
    if not os.path.exists(image_1):
        raise FileNotFoundError(f"Image {image_1} does not exist")
    if not os.path.exists(image_2):
        raise FileNotFoundError(f"Image {image_2} does not exist")

    # load input images
    imageA = cv2.imread(image_1)
    imageB = cv2.imread(image_2)

    # convert the images to grayscale
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # Compute the Structural Similarity Index (SSIM) between the two
    # images, ensuring that the difference image is returned
    (score, diff) = structural_similarity(grayA, grayB, full=True)
    if diff_file_path:
        diff = (diff * 255).astype("uint8") # Convert resulting array to an unsigned integer
        cv2.imwrite(diff_file_path, diff)

    # threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    if thresh_file_path:
        thresh = cv2.threshold(diff, 0, 255,
            cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        # loop over the contours
        for c in cnts:
            # compute the bounding box of the contour and then draw the
            # bounding box on both input images to represent where the two
            # images differ
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(imageA, (x, y), (x + w, y + h), (0, 0, 255), 2)
            cv2.rectangle(imageB, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv2.imwrite(thresh_file_path, thresh)
    difference = float(f"{((1-score)*100):.3f}")
    return difference
