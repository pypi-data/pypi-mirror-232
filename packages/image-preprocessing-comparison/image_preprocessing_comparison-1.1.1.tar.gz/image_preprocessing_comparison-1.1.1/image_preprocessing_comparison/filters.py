import cv2
import numpy as np


def convert_to_grayscale(image):
    """
    Convert the image to grayscale.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def convert_to_hsv(image):
    """
    Convert the image to HSV color space.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2HSV)


def convert_to_lab(image):
    """
    Convert the image to CIELAB color space.
    """
    return cv2.cvtColor(image, cv2.COLOR_BGR2LAB)


def apply_gaussian_blur(image, kernel_size):
    """
    Apply Gaussian blur to the image.
    """
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), 0)


def apply_median_blur(image, kernel_size):
    """
    Apply median blur to the image for noise reduction.
    """
    return cv2.medianBlur(image, kernel_size)


def apply_bilateral_filter(image):
    """
    Apply bilateral filter for noise reduction while preserving edges.
    """
    return cv2.bilateralFilter(image, d=9, sigmaColor=75, sigmaSpace=75)


def apply_binary_threshold(image, threshold_value, max_value):
    """
    Apply binary thresholding to create a binary image.
    """
    ret, threshold_image = cv2.threshold(image, threshold_value, max_value, cv2.THRESH_BINARY)
    return threshold_image


def apply_canny_edge_detection(image, min_threshold, max_threshold):
    """
    Apply Canny edge detection to the image.
    """
    return cv2.Canny(image, min_threshold, max_threshold)


def apply_dilation(image, kernel_size):
    """
    Apply dilation to enhance features in the image.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    return cv2.dilate(image, kernel, iterations=1)


def apply_erosion(image, kernel_size):
    """
    Apply erosion to reduce noise in the image.
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_size, kernel_size))
    return cv2.erode(image, kernel, iterations=1)


def apply_histogram_equalization(image):
    """
    Apply histogram equalization to improve contrast.
    """
    return cv2.equalizeHist(image)


def standardize_image(image):
    """
    Standardize pixel values (zero mean, unit variance).
    """
    mean, std_dev = cv2.meanStdDev(image)
    return (image - mean) / std_dev


def select_roi(image, top_left, bottom_right):
    """
    Crop the image to a specific region of interest (ROI).
    """
    return image[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]


def apply_custom_edge_enhancement(image):
    """
    Apply a custom edge enhancement filter to the image.
    """
    custom_kernel = [[-1, -1, -1],
                     [-1, 9, -1],
                     [-1, -1, -1]]

    custom_kernel = np.array(custom_kernel, dtype=np.float32)
    custom_kernel /= 9  # Normalize the kernel

    return cv2.filter2D(image, -1, custom_kernel)


def apply_custom_filter(image, kernel):
    """
    Apply a custom filter to the image.

    Parameters:
        image (np.ndarray): Input image.
        kernel (np.ndarray): Custom filter kernel.

    Returns:
        np.ndarray: Filtered image.
    """
    return cv2.filter2D(image, -1, kernel)


def draw_rectangle(image, top_left, bottom_right, color=(0, 255, 0), thickness=2):
    """
    Draw a rectangle on the image.

    Parameters:
        image (np.ndarray): Input image.
        top_left (tuple): Top-left corner coordinates of the rectangle (x, y).
        bottom_right (tuple): Bottom-right corner coordinates of the rectangle (x, y).
        color (tuple, optional): Color of the rectangle (B, G, R).
        thickness (int, optional): Thickness of the rectangle border.

    Returns:
        np.ndarray: Image with rectangle drawn.
    """
    return cv2.rectangle(image, top_left, bottom_right, color, thickness)


def draw_circle(image, center, radius, color=(0, 255, 0), thickness=2):
    """
    Draw a circle on the image.

    Parameters:
        image (np.ndarray): Input image.
        center (tuple): Center coordinates of the circle (x, y).
        radius (int): Radius of the circle.
        color (tuple, optional): Color of the circle (B, G, R).
        thickness (int, optional): Thickness of the circle border.

    Returns:
        np.ndarray: Image with circle drawn.
    """
    return cv2.circle(image, center, radius, color, thickness)


def draw_text(image, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.5, color=(0, 255, 0), thickness=1):
    """
    Draw text on the image.

    Parameters:
        image (np.ndarray): Input image.
        text (str): Text to be drawn.
        position (tuple): Position of the text (x, y).
        font (int, optional): Font type (e.g., cv2.FONT_HERSHEY_SIMPLEX).
        font_scale (float, optional): Font scale factor.
        color (tuple, optional): Color of the text (B, G, R).
        thickness (int, optional): Thickness of the text.

    Returns:
        np.ndarray: Image with text drawn.
    """
    return cv2.putText(image, text, position, font, font_scale, color, thickness)


def calculate_mse(image1, image2):
    """
    Calculate the Mean Squared Error (MSE) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: Mean Squared Error value.
    """
    squared_diff = (image1 - image2) ** 2
    mse = np.mean(squared_diff)
    return mse


def apply_sobel_filter(image, ksize=3):
    """
    Apply Sobel filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the Sobel kernel.

    Returns:
        np.ndarray: Edge-detected image.
    """
    return cv2.Sobel(image, cv2.CV_64F, 1, 1, ksize=ksize)


def apply_scharr_filter(image):
    """
    Apply Scharr filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Edge-detected image.
    """
    return cv2.Scharr(image, cv2.CV_64F, 1, 0) + cv2.Scharr(image, cv2.CV_64F, 0, 1)


def apply_prewitt_filter(image):
    """
    Apply Prewitt filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Edge-detected image.
    """
    kernelx = np.array([[-1, 0, 1], [-1, 0, 1], [-1, 0, 1]])
    kernely = np.array([[-1, -1, -1], [0, 0, 0], [1, 1, 1]])
    img_prewittx = cv2.filter2D(image, -1, kernelx)
    img_prewitty = cv2.filter2D(image, -1, kernely)
    return img_prewittx + img_prewitty


def apply_gaussian_filter(image, ksize=5):
    """
    Apply Gaussian filter for blurring and noise reduction.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the Gaussian kernel.

    Returns:
        np.ndarray: Blurred image.
    """
    return cv2.GaussianBlur(image, (ksize, ksize), 0)


def apply_laplacian_filter(image):
    """
    Apply Laplacian filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Edge-detected image.
    """
    return cv2.Laplacian(image, cv2.CV_64F)


def apply_emboss_filter(image):
    """
    Apply Emboss filter for creating a 3D effect.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Embossed image.
    """
    kernel = np.array([[-2, -1, 0], [-1, 1, 1], [0, 1, 2]])
    return cv2.filter2D(image, -1, kernel)


def apply_box_filter(image, ksize=5):
    """
    Apply Box filter for blurring.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the box filter kernel.

    Returns:
        np.ndarray: Blurred image.
    """
    return cv2.boxFilter(image, -1, (ksize, ksize))


def apply_motion_blur_filter(image, ksize=15):
    """
    Apply Motion Blur filter for simulating motion blur effect.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the motion blur kernel.

    Returns:
        np.ndarray: Blurred image.
    """
    kernel = np.zeros((ksize, ksize))
    kernel[int((ksize - 1) / 2), :] = np.ones(ksize)
    kernel = kernel / ksize
    return cv2.filter2D(image, -1, kernel)


def apply_bilateral_filter(image, d=9, sigma_color=75, sigma_space=75):
    """
    Apply Bilateral filter for noise reduction while preserving edges.

    Parameters:
        image (np.ndarray): Input image.
        d (int, optional): Diameter of each pixel neighborhood.
        sigma_color (float, optional): Filter sigma in the color space.
        sigma_space (float, optional): Filter sigma in the coordinate space.

    Returns:
        np.ndarray: Filtered image.
    """
    return cv2.bilateralFilter(image, d, sigma_color, sigma_space)


def apply_gabor_filter(image, frequency=0.6, theta=0, kernel_size=3):
    """
    Apply Gabor filter for texture analysis.

    Parameters:
        image (np.ndarray): Input image.
        frequency (float, optional): Frequency of the Gabor filter.
        theta (float, optional): Orientation of the Gabor filter.
        kernel_size (int, optional): Size of the Gabor kernel.

    Returns:
        np.ndarray: Filtered image.
    """
    g_kernel = cv2.getGaborKernel((kernel_size, kernel_size), frequency, theta, 10.0, 0.5, 0, ktype=cv2.CV_32F)
    return cv2.filter2D(image, cv2.CV_8UC3, g_kernel)


def apply_dog_filter(image, ksize1=5, ksize2=9):
    """
    Apply Difference of Gaussians (DoG) filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.
        ksize1 (int, optional): Size of the first Gaussian kernel.
        ksize2 (int, optional): Size of the second Gaussian kernel.

    Returns:
        np.ndarray: Edge-detected image.
    """
    dog = cv2.GaussianBlur(image, (ksize1, ksize1), 0) - cv2.GaussianBlur(image, (ksize2, ksize2), 0)
    return dog


def apply_log_filter(image, ksize=5):
    """
    Apply Laplacian of Gaussian (LoG) filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the LoG kernel.

    Returns:
        np.ndarray: Edge-detected image.
    """
    return cv2.Laplacian(cv2.GaussianBlur(image, (ksize, ksize), 0), cv2.CV_64F)


def apply_kirsch_operator(image):
    """
    Apply Kirsch Operator for edge detection.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Edge-detected image.
    """
    kirsch_masks = [
        [[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]],
        [[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]],
        [[5, 5, 5], [-3, 0, -3], [-3, -3, -3]],
        [[5, 5, -3], [5, 0, -3], [-3, -3, -3]],
        [[5, -3, -3], [5, 0, -3], [5, -3, -3]],
        [[-3, -3, -3], [5, 0, -3], [5, 5, -3]],
        [[-3, -3, -3], [-3, 0, -3], [5, 5, 5]],
        [[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]]
    ]

    result = np.zeros_like(image, dtype=np.float32)

    for mask in kirsch_masks:
        convolution = cv2.filter2D(image, -1, np.array(mask))
        np.maximum(result, convolution, out=result)

    return result


def apply_craigs_edge_detection(image):
    """
    Apply Craig's Edge Detection for edge detection.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Edge-detected image.
    """
    craigs_mask = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    return cv2.filter2D(image, -1, np.array(craigs_mask))


def apply_frei_chen_filter(image):
    """
    Apply Frei-Chen filter for edge detection.

    Parameters:
        image (np.ndarray): Input image.

    Returns:
        np.ndarray: Edge-detected image.
    """
    frei_chen_mask = [
        [[-1, -np.sqrt(2), -1], [0, 0, 0], [1, np.sqrt(2), 1]],
        [[-1, 0, 1], [-np.sqrt(2), 0, np.sqrt(2)], [-1, 0, 1]],
        [[1, np.sqrt(2), 1], [0, 0, 0], [-1, -np.sqrt(2), -1]],
        [[1, 0, -1], [np.sqrt(2), 0, -np.sqrt(2)], [1, 0, -1]]
    ]

    result = np.zeros_like(image, dtype=np.float32)

    for mask in frei_chen_mask:
        convolution = cv2.filter2D(image, -1, np.array(mask))
        np.maximum(result, convolution, out=result)

    return result


def apply_mean_filter(image, ksize=3):
    """
    Apply Mean filter for blurring.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the Mean filter kernel.

    Returns:
        np.ndarray: Blurred image.
    """
    return cv2.blur(image, (ksize, ksize))


def apply_median_filter(image, ksize=3):
    """
    Apply Median filter for noise reduction.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the Median filter kernel.

    Returns:
        np.ndarray: Filtered image.
    """
    return cv2.medianBlur(image, ksize)


def apply_min_filter(image, ksize=3):
    """
    Apply Min filter for reducing noise and enhancing edges.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the Min filter kernel.

    Returns:
        np.ndarray: Filtered image.
    """
    kernel = np.ones((ksize, ksize), np.float32) / (ksize ** 2)
    return cv2.filter2D(image, -1, kernel)


def apply_max_filter(image, ksize=3):
    """
    Apply Max filter for reducing noise and enhancing edges.

    Parameters:
        image (np.ndarray): Input image.
        ksize (int, optional): Size of the Max filter kernel.

    Returns:
        np.ndarray: Filtered image.
    """
    return cv2.dilate(image, np.ones((ksize, ksize), np.uint8))
