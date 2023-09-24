import cv2
import numpy as np
from scipy.stats import pearsonr
from skimage.metrics import structural_similarity
from skimage.metrics import structural_similarity as ssim
from sklearn.metrics import mean_squared_error
np.seterr(divide='ignore', invalid='ignore')


def ssim_comparison(image_path1, image_path2):
    """
    Performs the image comparison and visualization.
    Saves images in 640 by 640 resolution.
    :param image_path1: First input image.
    :param image_path2: Second input image.
    :return: Images after comparison.
    """
    before = cv2.imread(image_path1)
    after = cv2.imread(image_path2)

    # Resize images to 640x640
    before = cv2.resize(before, (640, 640))
    after = cv2.resize(after, (640, 640))

    # Convert images to grayscale
    before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
    after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

    # Compute SSIM between two images
    (score, diff) = structural_similarity(before_gray, after_gray, full=True)
    print("Image similarity:", score)

    # The diff image contains the actual image differences between the two images
    # and is represented as a floating point data type in the range [0,1]
    # so we must convert the array to 8-bit unsigned integers in the range
    # [0,255] before we can use it with OpenCV
    diff = (diff * 255).astype("uint8")

    # Threshold the difference image, followed by finding contours to
    # obtain the regions of the two input images that differ
    thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
    contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]

    mask = np.zeros(before.shape, dtype='uint8')
    filled_after = after.copy()

    for c in contours:
        area = cv2.contourArea(c)
        if area > 40:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(before, (x, y), (x + w, y + h), (36, 255, 12), 2)
            cv2.rectangle(after, (x, y), (x + w, y + h), (36, 255, 12), 2)
            cv2.drawContours(mask, [c], 0, (0, 255, 0), -1)
            cv2.drawContours(filled_after, [c], 0, (0, 255, 0), -1)

    # Save the images
    cv2.imwrite('before_comparison.png', before)
    cv2.imwrite('after_comparison.png', after)
    cv2.imwrite('difference.png', diff)
    cv2.imwrite('mask.png', mask)
    cv2.imwrite('filled_after.png', filled_after)

    return before, after, diff, mask, filled_after


def calculate_psnr(image1, image2):
    """
    Calculate Peak Signal-to-Noise Ratio (PSNR) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: PSNR value.
    """
    mse = mean_squared_error(image1, image2)
    max_pixel = np.max(image1)
    return 10 * np.log10((max_pixel ** 2) / mse)


def calculate_rmse(image1, image2):
    """
    Calculate Root Mean Square Error (RMSE) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: RMSE value.
    """
    return np.sqrt(np.mean((image1 - image2) ** 2))


def calculate_ncc(image1, image2):
    """
    Calculate Normalized Cross-Correlation (NCC) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: NCC value.
    """
    return np.sum((image1 - np.mean(image1)) * (image2 - np.mean(image2))) / \
        np.sqrt(np.sum((image1 - np.mean(image1)) ** 2) * np.sum((image2 - np.mean(image2)) ** 2))


def calculate_correlation_coefficient(image1, image2):
    """
    Calculate Correlation Coefficient between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: Correlation Coefficient value.
    """
    corr, _ = pearsonr(image1.flatten(), image2.flatten())
    return corr


def calculate_mae(image1, image2):
    """
    Calculate Mean Absolute Error (MAE) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: MAE value.
    """
    return np.mean(np.abs(image1 - image2))


def calculate_structural_content(image1, image2):
    """
    Calculate Structural Content (SC) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: SC value.
    """
    diff = image1 - image2
    return np.sum(np.abs(diff)) / np.sum(np.abs(image1))


def calculate_histogram_intersection(image1, image2):
    """
    Calculate Histogram Intersection between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: Histogram Intersection value.
    """
    hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_INTERSECT)


def calculate_kl_divergence(image1, image2):
    """
    Calculate Kullback-Leibler (KL) Divergence between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: KL Divergence value.
    """
    hist1 = cv2.calcHist([image1], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([image2], [0], None, [256], [0, 256])
    return cv2.compareHist(hist1, hist2, cv2.HISTCMP_KL_DIV)


def calculate_f1_score(image1, image2):
    """
    Calculate F1 Score between two binary images.

    Parameters:
        image1 (np.ndarray): First input binary image.
        image2 (np.ndarray): Second input binary image.

    Returns:
        float: F1 Score value.
    """
    intersection = np.logical_and(image1, image2)
    precision = np.sum(intersection) / np.sum(image1)
    recall = np.sum(intersection) / np.sum(image2)
    return 2 * (precision * recall) / (precision + recall)


def calculate_dice_coefficient(image1, image2):
    """
    Calculate Dice Coefficient between two binary images.

    Parameters:
        image1 (np.ndarray): First input binary image.
        image2 (np.ndarray): Second input binary image.

    Returns:
        float: Dice Coefficient value.
    """
    intersection = np.logical_and(image1, image2)
    return 2 * np.sum(intersection) / (np.sum(image1) + np.sum(image2))


def calculate_jaccard_index(image1, image2):
    """
    Calculate Jaccard Index (Intersection over Union) between two binary images.

    Parameters:
        image1 (np.ndarray): First input binary image.
        image2 (np.ndarray): Second input binary image.

    Returns:
        float: Jaccard Index value.
    """
    intersection = np.logical_and(image1, image2)
    union = np.logical_or(image1, image2)
    return np.sum(intersection) / np.sum(union)


def calculate_mean_absolute_percentage_error(image1, image2):
    """
    Calculate Mean Absolute Percentage Error (MAPE) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: MAPE value.
    """
    return np.mean(np.abs((image1 - image2) / image1)) * 100


def calculate_zero_mean_normalized_cross_correlation(image1, image2):
    """
    Calculate Zero-Mean Normalized Cross-Correlation (ZNCC) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: ZNCC value.
    """
    return np.sum((image1 - np.mean(image1)) * (image2 - np.mean(image2))) / \
        np.sqrt(np.sum((image1 - np.mean(image1)) ** 2) * np.sum((image2 - np.mean(image2)) ** 2))


def calculate_pixelwise_mse(image1, image2):
    """
    Calculate Pixel-wise Mean Squared Error (MSE) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        np.ndarray: Pixel-wise MSE image.
    """
    return (image1 - image2) ** 2


def calculate_multi_scale_ssim(image1, image2):
    """
    Calculate Multi-Scale Structural Similarity Index (MS-SSIM) between two images.

    Parameters:
        image1 (np.ndarray): First input image.
        image2 (np.ndarray): Second input image.

    Returns:
        float: MS-SSIM value.
    """
    return ssim(image1, image2, multichannel=True)
