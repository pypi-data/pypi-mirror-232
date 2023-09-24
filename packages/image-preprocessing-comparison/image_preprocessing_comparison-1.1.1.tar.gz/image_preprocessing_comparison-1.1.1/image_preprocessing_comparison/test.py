# import cv2
# from skimage.metrics import structural_similarity as ssim
#
# from compare_images import calculate_psnr, calculate_rmse, calculate_ncc, calculate_correlation_coefficient, \
#     calculate_mae, calculate_structural_content, calculate_histogram_intersection, \
#     calculate_kl_divergence, calculate_f1_score, calculate_dice_coefficient, \
#     calculate_jaccard_index, calculate_mean_absolute_percentage_error, calculate_zero_mean_normalized_cross_correlation, \
#     calculate_multi_scale_ssim, ssim_comparison
#
# # Load two example images for testing
# image1 = cv2.imread('image1.jpg', cv2.IMREAD_GRAYSCALE)
# image2 = cv2.imread('image2.jpg', cv2.IMREAD_GRAYSCALE)
#
# # Calculate SSIM using skimage.metrics
# ssim_value = ssim(image1, image2)
#
# # List of comparison functions
# comparison_functions = [
#     calculate_psnr,
#     calculate_rmse,
#     calculate_ncc,
#     calculate_correlation_coefficient,
#     calculate_mae,
#     calculate_structural_content,
#     calculate_histogram_intersection,
#     calculate_kl_divergence,
#     calculate_f1_score,
#     calculate_dice_coefficient,
#     calculate_jaccard_index,
#     calculate_mean_absolute_percentage_error,
#     calculate_zero_mean_normalized_cross_correlation,
#     calculate_multi_scale_ssim
# ]
#
# # Test and print results for each comparison function
# for func in comparison_functions:
#     result = func(image1, image2)
#     print(f"{func.__name__}: {result}")
#
# print(f"SSIM (using skimage.metrics): {ssim_value}")
#
# ssim_comparison(image_path1='image1.jpg', image_path2='image2.jpg')

import cv2
import numpy as np

from filters import apply_sobel_filter, apply_scharr_filter, apply_prewitt_filter, apply_gaussian_filter, \
    apply_laplacian_filter, apply_emboss_filter, apply_box_filter, apply_motion_blur_filter, apply_bilateral_filter, \
    apply_gabor_filter, apply_dog_filter, apply_log_filter, apply_kirsch_operator, apply_craigs_edge_detection, \
    apply_frei_chen_filter, apply_mean_filter, apply_median_filter, apply_min_filter, \
    apply_max_filter


def test_all_filters(input_image):
    sobel_result = apply_sobel_filter(input_image)
    scharr_result = apply_scharr_filter(input_image)
    prewitt_result = apply_prewitt_filter(input_image)
    gaussian_result = apply_gaussian_filter(input_image)
    laplacian_result = apply_laplacian_filter(input_image)
    emboss_result = apply_emboss_filter(input_image)
    box_result = apply_box_filter(input_image)
    motion_blur_result = apply_motion_blur_filter(input_image)
    bilateral_result = apply_bilateral_filter(input_image)
    gabor_result = apply_gabor_filter(input_image)
    dog_result = apply_dog_filter(input_image)
    log_result = apply_log_filter(input_image)
    kirsch_result = apply_kirsch_operator(input_image)
    craigs_result = apply_craigs_edge_detection(input_image)
    frei_chen_result = apply_frei_chen_filter(input_image)
    mean_result = apply_mean_filter(input_image)
    median_result = apply_median_filter(input_image)
    min_result = apply_min_filter(input_image)
    max_result = apply_max_filter(input_image)

    return {
        "Sobel Filter": sobel_result,
        "Scharr Filter": scharr_result,
        "Prewitt Filter": prewitt_result,
        "Gaussian Filter": gaussian_result,
        "Laplacian Filter": laplacian_result,
        "Emboss Filter": emboss_result,
        "Box Filter": box_result,
        "Motion Blur Filter": motion_blur_result,
        "Bilateral Filter": bilateral_result,
        "Gabor Filter": gabor_result,
        "Difference of Gaussians (DoG) Filter": dog_result,
        "Laplacian of Gaussian (LoG) Filter": log_result,
        "Kirsch Operator": kirsch_result,
        "Craig's Edge Detection": craigs_result,
        "Frei-Chen Filter": frei_chen_result,
        "Mean Filter": mean_result,
        "Median Filter": median_result,
        "Min Filter": min_result,
        "Max Filter": max_result
    }


# Usage example:
input_image = cv2.imread('image1.jpg', cv2.IMREAD_GRAYSCALE)
filtered_images = test_all_filters(input_image)

# Display and save the filtered images
for filter_name, result in filtered_images.items():
    cv2.imwrite(f'{filter_name}.jpg', result)

