#!/usr/bin/env python3

import math
from PIL import Image


# FUNCTIONS FROM PT.1

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


# HELPER FUNCTIONS FROM LAB 1


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


# FILTERS FROM LAB 1


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


# VARIOUS FILTERS


def separate(image):  # NEED TO MAKE FASTER
    """
    Given an image, returns a dictionary of separate lists of red values,
    green values, and blue values of the given image. 
    """
    pixel = image["pixels"].copy()
    r_list = []
    g_list = []
    b_list = []
    for r, g, b in pixel:
        r_list.append(r)
        g_list.append(g)
        b_list.append(b)
    return {"red": r_list, "green": g_list, "blue": b_list}


def combine(r_im, g_im, b_im):
    """ 
    Given three images, each corresponding to red, green, or blue
    values, returns a combined image of the three.

    Undoes the separate function.
    """
    r_pixel = r_im["pixels"].copy()
    g_pixel = g_im["pixels"].copy()
    b_pixel = b_im["pixels"].copy()
    combined_pixel = list(zip(r_pixel, g_pixel, b_pixel))
    return {"height": r_im["height"], "width": r_im["width"], "pixels": combined_pixel}


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """

    def create_filtered_image(image):
        rbg_dict = separate(image)
        r_image = {
            "height": image["height"],
            "width": image["width"],
            "pixels": rbg_dict["red"],
        }
        g_image = {
            "height": image["height"],
            "width": image["width"],
            "pixels": rbg_dict["green"],
        }
        b_image = {
            "height": image["height"],
            "width": image["width"],
            "pixels": rbg_dict["blue"],
        }
        r_new = filt(r_image)
        g_new = filt(g_image)
        b_new = filt(b_image)
        return combine(r_new, g_new, b_new)

    return create_filtered_image


def make_blur_filter(kernel_size):
    def blur_filter(image):
        return blurred(image, kernel_size)

    return blur_filter


def make_sharpen_filter(kernel_size):
    def sharpen_filter(image):
        return sharpened(image, kernel_size)

    return sharpen_filter


def make_edges_filter(kernel_size):
    def edges_filter(image):
        return edges(image, kernel_size)

    return edges_filter


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """

    def filt(image):
        new_image = image.copy()
        for filter in filters:
            new_image = filter(new_image)
        return new_image

    return filt


# SEAM CARVING

# Main Seam Carving Implementation


def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image. Returns a new image.
    """
    new_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": image["pixels"].copy(),
    }
    for i in range(ncols):
        seam = minimum_energy_seam(
            cumulative_energy_map(
                compute_energy(greyscale_image_from_color_image(new_image))
            )
        )
        new_image = image_without_seam(new_image, seam)
    return new_image


# Optional Helper Functions for Seam Carving


def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    new_pixel = []
    for r, g, b in image["pixels"]:
        new_pixel.append(round(0.299 * r + 0.587 * g + 0.114 * b))
    return {"height": image["height"], "width": image["width"], "pixels": new_pixel}


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    return edges(grey)


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy
    function), computes a "cumulative energy map" as described in the lab 2
    writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    num_row = energy["height"]
    num_col = energy["width"]
    new_energy = energy.copy()
    pixel = new_energy["pixels"].copy()
    new_energy["pixels"] = pixel

    for row in range(num_row):
        for col in range(num_col):
            if row == 0:
                continue
            elif col == 0:
                minimum = min(
                    get_pixel(new_energy, row - 1, col, None),
                    get_pixel(new_energy, row - 1, col + 1, None),
                )
            elif col == num_col - 1:
                minimum = min(
                    get_pixel(new_energy, row - 1, col - 1, None),
                    get_pixel(new_energy, row - 1, col, None),
                )
            else:
                minimum = min(
                    get_pixel(new_energy, row - 1, col - 1, None),
                    get_pixel(new_energy, row - 1, col, None),
                    get_pixel(new_energy, row - 1, col + 1, None),
                )
            set_pixel(
                new_energy, row, col, get_pixel(new_energy, row, col, None) + minimum
            )
    return {"height": energy["height"], "width": energy["width"], "pixels": pixel}


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    num_row = cem["height"]
    num_col = cem["width"]
    cem_copy = cem.copy()
    bottom_index_list = []

    bottom_row = []
    for col in range(num_col):
        bottom_row.append(get_pixel(cem_copy, num_row - 1, col, None))
        bottom_index_list.append(num_col * num_row - (num_col - col))

    bottom_min_val = min(bottom_row)
    min_index = bottom_index_list[bottom_row.index(bottom_min_val)]

    index_list = [min_index]

    min_row = min_index // num_col
    min_col = min_index % num_col

    for row in range(num_row - 1):
        new_row = min_row - row - 1
        if min_col == 0:
            minimum = min(
                get_pixel(cem_copy, new_row, min_col, None),
                get_pixel(cem_copy, new_row, min_col + 1, None),
            )
            index_list.append(cem_copy["pixels"].index(minimum, min_index - num_col))

        elif min_col == num_col - 1:
            minimum = min(
                get_pixel(cem_copy, new_row, min_col - 1, None),
                get_pixel(cem_copy, new_row, min_col, None),
            )
            index_list.append(
                cem_copy["pixels"].index(minimum, min_index - num_col - 1)
            )

        else:
            minimum = min(
                get_pixel(cem_copy, new_row, min_col - 1, None),
                get_pixel(cem_copy, new_row, min_col, None),
                get_pixel(cem_copy, new_row, min_col + 1, None),
            )
            index_list.append(
                cem_copy["pixels"].index(minimum, min_index - num_col - 1)
            )

        min_col = index_list[-1] % num_col
        min_index = index_list[-1]
    return index_list


def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    new_image = image.copy()
    new_pixel = [value for i, value in enumerate(new_image["pixels"]) if i not in seam]
    return {"height": image["height"], "width": image["width"] - 1, "pixels": new_pixel}


def custom_feature(image):
    """
    Given a color image, return a new image where the top third of the image is
    just red values, middle is blue values, and bottom is green values.
    """
    rbg_dict = separate(image)
    r_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": rbg_dict["red"],
    }
    g_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": rbg_dict["green"],
    }
    b_image = {
        "height": image["height"],
        "width": image["width"],
        "pixels": rbg_dict["blue"],
    }

    new_r = []
    new_g = []
    new_b = []

    length = len(r_image["pixels"])

    for pix in range(length):
        if len(new_r) <= length // 3:
            new_r.append(r_image["pixels"][pix])
            new_b.append(0)
            new_g.append(0)
        elif len(new_g) > length // 3 and len(new_g) <= 2 * (length // 3):
            new_r.append(0)
            new_g.append(g_image["pixels"][pix])
            new_b.append(0)
        else:
            new_r.append(0)
            new_g.append(0)
            new_b.append(b_image["pixels"][pix])

    r_im = {"height": image["height"], "width": image["width"], "pixels": new_r}
    b_im = {"height": image["height"], "width": image["width"], "pixels": new_b}
    g_im = {"height": image["height"], "width": image["width"], "pixels": new_g}

    return combine(r_im, g_im, b_im)



# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES


def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, "rb") as img_handle:
        img = Image.open(img_handle)
        img = img.convert("RGB")  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        width, height = img.size
        return {"height": height, "width": width, "pixels": pixels}


def save_color_image(image, filename, mode="PNG"):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode="RGB", size=(image["width"], image["height"]))
    out.putdata(image["pixels"])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


def load_greyscale_image(filename):
    """
    Loads an image from the given file and returns an instance of this class
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_greyscale_image('test_images/cat.png')
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
    by the 'mode' parameter.
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

    # cat = load_color_image("test_images/cat.png")
    # create_filtered_image = color_filter_from_greyscale_filter(inverted)
    # inverted_color_cat = create_filtered_image(cat)
    # save_color_image(inverted_color_cat, "inverted_color_cat.png")

    # python = load_color_image("test_images/python.png")
    # create_filtered_image = color_filter_from_greyscale_filter(make_blur_filter(9))
    # blurry_python = create_filtered_image(python)
    # save_color_image(blurry_python, "blurry_python.png")

    # sparrowchick = load_color_image("test_images/sparrowchick.png")
    # create_filtered_image = color_filter_from_greyscale_filter(make_sharpen_filter(7))
    # sharpened_sparrowchick = create_filtered_image(sparrowchick)
    # save_color_image(sharpened_sparrowchick, "sharpened_sparrowchick.png")

    # frog = load_color_image("test_images/frog.png")
    # filter1 = color_filter_from_greyscale_filter(edges)
    # filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    # filt = filter_cascade([filter1, filter1, filter2, filter1])
    # filtered_frog = filt(frog)
    # save_color_image(filtered_frog, "filtered_frog.png")

    # cem = {'width': 9, 'height': 4, 'pixels': [160, 160, 0, 28, 0, 28, 0, 160, 160, 415, 218, 10, 22, 14, 22, 10, 218, 415, 473, 265, 40, 10, 28, 10, 40, 265, 473, 520, 295, 41, 32, 10, 32, 41, 295, 520]}
    # print(minimum_energy_seam(cem))

    # frog = load_color_image("test_images/frog.png")
    # save_color_image(custom_feature(frog), "rbg_frog.png")

    # two_cats = load_color_image("test_images/twocats.png")
    # save_color_image(seam_carving(two_cats, 100), "seam_two_cats.png")

    # flood = load_color_image("test_images/flood_input.png")
    # print(flood["height"], flood["width"])
    pass
