import cv2
import numpy as np
import glob
#import matplotlib.pyplot as plt
import time


'''

한 개의 image당 처리 속도: 약 0.05sec

'''

# selected threshold to highlight yellow lines
yellow_HSV_th_min = np.array([0, 70, 70])
yellow_HSV_th_max = np.array([50, 255, 255])


def thresh_frame_in_HSV(frame, min_values, max_values, verbose=False):
    """
    Threshold a color frame in HSV space
    """
    HSV = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    min_th_ok = np.all(HSV > min_values, axis=2)
    max_th_ok = np.all(HSV < max_values, axis=2)

    out = np.logical_and(min_th_ok, max_th_ok)

    #if verbose:
    #plt.imshow(out, cmap='gray')
    #plt.show()

    return out


def thresh_frame_sobel(frame, kernel_size):
    """
    Apply Sobel edge detection to an input frame, then threshold the result
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    #gray = frame

    sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=kernel_size)
    sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=kernel_size)

    sobel_mag = np.sqrt(sobel_x ** 2 + sobel_y ** 2)
    sobel_mag = np.uint8(sobel_mag / np.max(sobel_mag) * 255)

    _, sobel_mag = cv2.threshold(sobel_mag, 70, 255, cv2.THRESH_BINARY)

    return sobel_mag.astype(bool)


def get_binary_from_equalized_grayscale(frame):
    """
    Apply histogram equalization to an input frame, threshold it and return the (binary) result.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    eq_global = cv2.equalizeHist(gray)

    _, th = cv2.threshold(eq_global, thresh=240, maxval=255, type=cv2.THRESH_BINARY)

    return th


def binarize(img, verbose=False):
    """
    Convert an input frame to a binary image which highlight as most as possible the lane-lines.

    :param img: input color frame
    :param verbose: if True, show intermediate results
    :return: binarized frame
    """

    h, w = img.shape[:2]
    binary = np.zeros(shape=(h, w), dtype=np.uint8)

    # highlight yellow lines by threshold in HSV color space
    # HSV_yellow_mask = thresh_frame_in_HSV(img, yellow_HSV_th_min, yellow_HSV_th_max, verbose=False)
    # binary = np.logical_or(binary, HSV_yellow_mask)

    # highlight white lines by thresholding the equalized frame
    eq_white_mask = get_binary_from_equalized_grayscale(img)
    binary = np.logical_or(binary, eq_white_mask)
    #print(binary)
    # get Sobel binary mask (thresholded gradients)
    sobel_mask = thresh_frame_sobel(img, kernel_size=5)
    binary = np.logical_or(binary, sobel_mask)
    #print(binary)
    # apply a light morphology to "fill the gaps" in the binary image
    closing_kernel = np.ones((3, 3), np.uint8)
    #opening_kernel = np.ones((4, 3), np.uint8)
    closing = cv2.morphologyEx(binary.astype(np.uint8), cv2.MORPH_CLOSE, closing_kernel)
    #erosion = cv2.erode(closing, opening_kernel, iterations=2)

    return closing * 255


if __name__ == '__main__':

    test_images = glob.glob('test_images/*.jpg')

    start_time = time.time()

    for test_image in test_images:
        # img = cv2.imread('/home/pirl/self-driving-car/project_4_advanced_lane_finding/test_images/capture.jpg')
        img = cv2.imread(test_image)
        img = binarize(img=img, verbose=True)

        roi = img[500:720, 50:1200]
        # r = cv2.selectROI(img, fromCenter)
        cv2.imshow('img', img)
        cv2.imwrite('output_binary/{}'.format(test_image), roi)

        if cv2.waitKey(1) > 0: break

    print(time.time() - start_time)