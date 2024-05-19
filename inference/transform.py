import numpy as np
from PIL import Image
from PIL.JpegImagePlugin import JpegImageFile


class PILImageTransform:
    def __init__(self, transform_list: list) -> None:
        """
        A lightweight wrapper similar to torchvision.transform for Pillow images.
        :param transform_list: list of callables
        """
        self.transform_list = transform_list

    def __call__(self, image: Image.Image or JpegImageFile) -> np.array:
        """
        Make image transform
        :param image: Image.Image, JpegImageFile
        :return: np.array
        """
        for op in self.transform_list:
            image = op(image)
        return image


class Normalize:
    def __init__(self, mean: list, std: list) -> None:
        """
        Custom normalization similar to torchvision.transforms.Normalize
        :param mean: python list of floats
        :param std:  python list of floats
        """
        self.mean = np.array(mean, dtype=np.float32)
        self.std = np.array(std, dtype=np.float32)

    def __call__(self, image: np.array) -> np.array:
        """
        Standardize image
        :param image: np.array
        :return: np.array
        """
        channels = tuple(range(image.shape[0]))
        for ch in channels:
            image[ch] = (image[ch] - self.mean[ch]) / self.std[ch]
        return image


def get_input_transform(image_size: int, img_normalize: dict) -> PILImageTransform:
    """
    Get image transform pipeline for an input.
    This is a lightweight analogue of torchvision transform pipeline.
    [torchvision.transforms.Resize(size=(image_size, image_size)),
    torchvision.transforms.ToTensor(),
    torchvision.transforms.Normalize(mean=img_normalize['mean'], std=img_normalize['std'])]
    :param image_size:    int, image size for resizing
    :param img_normalize: dict with mean and std for image normalization
    :return:
    """

    transform_list = [
        lambda img: img.resize(size=(image_size, image_size), resample=Image.BILINEAR),
        lambda x: np.array(x, dtype=np.float32),
        lambda x: x.transpose((2, 0, 1)),
        lambda x: x / 255.0,
        Normalize(mean=img_normalize["mean"], std=img_normalize["std"]),
    ]

    return PILImageTransform(transform_list=transform_list)
