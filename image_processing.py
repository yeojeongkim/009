#!/usr/bin/env python3

import math

from PIL import Image

def get_pixel(image, row, col, boundary_behavior):
    """
    Return the value (at the given row and column) of the current
    pixel in the given image.

    Boundary_behavior determines what value to return at a row and column
    outside of the image height and width (image boundary).
    """
    num_row = image["height"]
    num_col = image["width"]
    pixel = image["pixels"]

    if row < 0 or col < 0 or row >= num_row or col >= num_col:
        if boundary_behavior == "zero":
            return 0

        elif boundary_behavior == "extend":
            new_row = 0
            new_col = 0
            if row > num_row - 1:
                new_row = num_row - 1
            elif row < 0:
                new_row = 0
            else:
                new_row = row
            if col > num_col - 1:
                new_col = num_col - 1
            elif col < 0:
                new_col = 0
            else:
                new_col = col
            return pixel[int(new_row * num_col + new_col)]

        elif boundary_behavior == "wrap":
            return pixel[(row % num_row) * num_col + (col % num_col)]
    else:
        return pixel[int(row * num_col + col)]


def set_pixel(image, row, col, color):
    """
    Modify one pixel value (at the given row and column) to a new color
    of a given image.
    """
    image["pixels"][row * image["width"] + col] = color


def apply_per_pixel(image, func):
    """
    Return a new image representing the result of the given function applied
    to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    result = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"].copy(),
    }
    for row in range(image["height"]):
        for col in range(image["width"]):
            color = get_pixel(image, row, col, None)
            new_color = func(color)
            set_pixel(result, row, col, new_color)
    return result


def inverted(image):
    """
    Return a new image representing the result of inverting the given input image.
    """
    return apply_per_pixel(image, lambda color: 255 - color)


# HELPER FUNCTIONS


def correlate(image, kernel, boundary_behavior):
    """
    Compute the result of correlating the given image with the given kernel.
    `boundary_behavior` will one of the strings "zero", "extend", or "wrap",
    and this function will treat out-of-bounds pixels as having the value zero,
    the value of the nearest edge, or the value wrapped around the other edge
    of the image, respectively.

    if boundary_behavior is not one of "zero", "extend", or "wrap", return
    None.

    Otherwise, the output of this function should have the same form as a 6.101
    image (a dictionary with "height", "width", and "pixels" keys), but its
    pixel values do not necessarily need to be in the range [0,255], nor do
    they need to be integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE
    The kernel is a 2D list, where there are lists inside a list. Each inner list represents
    one row of the kernel.
    """

    num_row = image["height"]
    num_col = image["width"]

    kernel_length = len(kernel)

    new_image_pixel = []

    if (
        boundary_behavior != "zero"
        and boundary_behavior != "extend"
        and boundary_behavior != "wrap"
    ):
        return None
    for row in range(num_row):
        for col in range(num_col):
            new_pixel = 0
            for y in range(kernel_length):
                for x in range(kernel_length):
                    new_col = col + x - kernel_length // 2
                    new_row = row + y - kernel_length // 2
                    val = (
                        get_pixel(image, new_row, new_col, boundary_behavior)
                        * kernel[y][x]
                    )
                    new_pixel += val
            new_image_pixel.append(new_pixel)

    return {"height": num_row, "width": num_col, "pixels": new_image_pixel}


def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the "pixels" list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    row = image["height"]
    column = image["width"]
    pixel = image["pixels"].copy()
    pixel = [int(round(x)) for x in pixel]
    new_pixel = []
    for value in pixel:
        if value < 0:
            new_pixel.append(0)
        elif value > 255:
            new_pixel.append(255)
        else:
            new_pixel.append(value)
    return {"height": row, "width": column, "pixels": new_pixel}


# FILTERS


def blurred(image, kernel_size):
    """
    Return a new image representing the result of applying a box blur (with the
    given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)

    # then compute the correlation of the input image with that kernel

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    kernel = [[1 / (kernel_size**2)] * kernel_size] * kernel_size
    correlation = correlate(image, kernel, "extend")
    return round_and_clip_image(correlation)


def sharpened(image, n):
    """
    Return a new image representing the result of applying a sharpen filter (with
    the given kernel size) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    pixel = image["pixels"].copy()
    blurred_image = blurred(image, n)
    sharpened_image_pixels = [
        (2 * pixel[i] - blurred_image["pixels"][i]) for i in range(len(image["pixels"]))
    ]
    return round_and_clip_image(
        {
            "height": image["height"],
            "width": image["width"],
            "pixels": sharpened_image_pixels,
        }
    )


def edges(image):
    """
    Return a new image representing the result of applying a filter called a 'Sobel
    Operator' to the given input image to detect edges.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    Krow = [[-1, -2, -1], [0, 0, 0], [1, 2, 1]]
    Kcol = [[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]

    correlate_Krow = correlate(image.copy(), Krow, "extend")
    correlate_Kcol = correlate(image.copy(), Kcol, "extend")

    edge_list = [
        round(
            math.sqrt(
                correlate_Krow["pixels"][i] ** 2 + correlate_Kcol["pixels"][i] ** 2
            )
        )
        for i in range(len(correlate_Krow["pixels"]))
    ]
    edge_dict = {
        "height": image["height"],
        "width": image["width"],
        "pixels": edge_list,
    }

    return round_and_clip_image(edge_dict)


# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image("test_images/cat.png")
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith("RGB"):
            pixels = [
                round(0.299 * p[0] + 0.587 * p[1] + 0.114 * p[2]) for p in img_data
            ]
        elif img.mode == "LA":
            pixels = [p[0] for p in img_data]
        elif img.mode == "L":
            pixels = list(img_data)
        else:
            raise ValueError(f"Unsupported image mode: {img.mode}")
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_greyscale_image(image, filename, mode="PNG"):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the "mode" parameter.
    """
    out = Image.new(mode="L", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == "__main__":
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.

    # bluegill = load_greyscale_image("test_images/bluegill.png")
    # save_greyscale_image(inverted(bluegill), "inverted_bluegill.png")

    # kernel = [
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    #     ]
    # pigbird = load_greyscale_image("test_images/pigbird.png")
    # save_greyscale_image(correlate(pigbird,kernel,"zero"), "zero_pigbird.png")
    # save_greyscale_image(correlate(pigbird,kernel,"extend"), "extend_pigbird.png")
    # save_greyscale_image(correlate(pigbird,kernel,"wrap"), "wrap_pigbird.png")

    # image = load_greyscale_image("test_images/cat.png")
    # save_greyscale_image(blurred(image,13), "blur_zero_cat.png")

    # image = load_greyscale_image("test_images/python.png")
    # save_greyscale_image(sharpened(image, 11), "sharpen_python.png")

    # image = load_greyscale_image("test_images/construct.png")
    # save_greyscale_image(edges(image), "edges_construct.png")

    # image = load_greyscale_image("test_images/centered_pixel.png")
    # print(edges(image))

    pass
