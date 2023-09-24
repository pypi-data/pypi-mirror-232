import cv2


def load_image(path):
    """
        Load an image from a given path.
    """
    return cv2.imread(path)


def save_image(image, path):
    """
        Save an image to a given path.
    """
    cv2.imwrite(path, image)


def resize_image(image, width, height):
    """
        Resize the image to the specified width and height.
    """
    return cv2.resize(image, (width, height))
