import math
from matplotlib import scale

import numpy as np
import pandas as pd
from PIL import Image

from ImageTools import check_similarity, scaleImage, to_mono
import compileImages
from Fractal import Fractal

# add test for compileImages.get_alternative_images

# taken from CSE163 utils
TOLERANCE = 0.001


def check_approx_equals(expected, received):
    """
    Checks received against expected, and returns whether or
    not they match (True if they do, False otherwise).
    If the argument is a float, will do an approximate check.
    If the arugment is a data structure will do an approximate check
    on all of its contents.
    """
    try:
        if type(expected) == dict:
            # first check that keys match, then check that the
            # values approximately match
            return expected.keys() == received.keys() and \
                all([check_approx_equals(expected[k], received[k])
                    for k in expected.keys()])
        elif type(expected) == list or type(expected) == set:
            # Checks both lists/sets contain the same values
            return len(expected) == len(received) and \
                all([check_approx_equals(v1, v2)
                    for v1, v2 in zip(expected, received)])
        elif type(expected) == float:
            return math.isclose(expected, received, abs_tol=TOLERANCE)
        elif type(expected) == np.ndarray:
            return np.allclose(expected, received, abs_tol=TOLERANCE,
                               equal_nan=True)
        elif type(expected) == pd.DataFrame:
            try:
                pd.testing.assert_frame_equal(expected, received,
                                              atol=TOLERANCE)
                return True
            except AssertionError:
                return False
        elif type(expected) == pd.Series:
            try:
                pd.testing.assert_series_equal(expected, received,
                                               atol=TOLERANCE)
                return True
            except AssertionError:
                return False
        else:
            return expected == received
    except Exception as e:
        print(f"EXCEPTION: Raised when checking check_approx_equals {e}")
        return False


def assert_equals(expected, received):
    """
    Checks received against expected, throws an AssertionError
    if they don't match. If the argument is a float, will do an approximate
    check. If the arugment is a data structure will do an approximate check
    on all of its contents.
    """

    if type(expected) == str:
        # Make sure strings have explicit quotes around them
        err_msg = f'Failed: Expected "{expected}", but received "{received}"'
    elif type(expected) in [np.ndarray, pd.Series, pd.DataFrame]:
        # Want to make multi-line output for data structures
        err_msg = f'Failed: Expected\n{expected}\n\nbut received\n{received}'
    else:
        err_msg = f'Failed: Expected {expected}, but received {received}'

    assert check_approx_equals(expected, received), err_msg


def test_image_tools():
    print("Running Image Tools Tests")

    circle = Image.open("test_imgs/circle.png")
    circle_copy = circle.copy()
    assert_equals(1, check_similarity(circle, circle_copy))

    red = Image.open("test_imgs/red.jpg")
    blue = Image.open("test_imgs/blue.png")
    assert_equals(0, check_similarity(red, blue))

    
    circle_scaled = Image.open("test_imgs/circle_scaled.png")
    circle_scaled_aspect = Image.open("test_imgs/circle_scaled_aspect.png")

    circle_scaled_calc = scaleImage(circle, (1200,500))
    circle_aspect_calc = scaleImage(circle, (1200,500), keep_aspect_ratio=True)

    assert_equals(1, check_similarity(circle_scaled_aspect, circle_aspect_calc))
    assert_equals(1, check_similarity(circle_scaled, circle_scaled_calc))

    circle_mono = Image.open("test_imgs/circle_mono.png")
    circle_mono_calc = to_mono(circle)

    assert_equals(1, check_similarity(circle_mono_calc, circle_mono))


def test_compile_images():
    # normalize_html
    print("testing compile images")
    text = compileImages.normalize_html("<a>test 12</a>3<span>test</span>")
    assert_equals("test 123", text)
    text = compileImages.normalize_html("test string")
    assert_equals("test string", text)

    # normalize_float
    num = compileImages.normalize_float("2.06 ±0.01")
    assert_equals(2.06, num)
    num = compileImages.normalize_float("2.06 test  ")
    assert_equals(2.06, num)
    num = compileImages.normalize_float("2")
    assert_equals(2, num)
    num = compileImages.normalize_float("2 <span>2other element</span>")
    assert_equals(2, num)

    # parse_image_html
    text = compileImages.parse_image_html("""<img src="//test.com">""")
    assert_equals("https://test.com", text)
    text = compileImages.parse_image_html("""extra\n<img src="//test.com">""")
    assert_equals("https://test.com", text)

    # get_image_from_url
    google = Image.open("test_imgs/google.png")
    URL = "https://www.google.com/images/branding/googlelogo/2x/"
    URL += "googlelogo_light_color_272x92dp.png"
    downloaded = compileImages.get_image_from_url(URL)
    assert_equals(1, check_similarity(google, downloaded))

    # format_file_name
    text = compileImages.format_file_name("test\image")
    assert_equals("testimage", text)
    text = compileImages.format_file_name("test\ image")
    assert_equals("test_image", text)
    text = compileImages.format_file_name("C:\\importantstuff\\test")
    assert_equals("Cimportantstufftest", text)


def test_fractal():
    print("Testing Fractal")
    f = Fractal("test_imgs/circle.png")
    f2 = Fractal("test_imgs/fractal.png")

    assert_equals((0,0,0,255), f._get_background_color(f._img))

    assert_equals([0,1, 1000, 1001], f._get_square_indicies(f._img, 0,0))
    assert_equals([999,1999], f._get_square_indicies(f._img, 999,0))

    assert_equals(1, f2._count_non_background_pixels(f2._img))

    assert_equals([(2,11)], f2._get_scaling_data(0, 1, 2, []))
    assert_equals([(1,1)], f2._get_scaling_data(0, 1, 1, []))

    assert_equals(0, f._get_mean_squared_error([(0,0), (1,1), (2,2)], 1, 0))
    assert_equals(1, f._get_mean_squared_error([(1,1)], 0, 0))

    assert_equals(1.0, f._calculate_best_slope([(0,0), (1,1), (2,2)]))
    assert_equals(2.0, f._calculate_best_slope([(0,0), (1,2), (2,4)]))

    f = Fractal("test_imgs/blue.png")
    assert_equals(0, f.calculate_power())


def main():
    test_image_tools()
    test_compile_images()
    test_fractal()

if "__main__" in __name__:
    main()