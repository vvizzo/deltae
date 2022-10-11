#!/usr/bin/python
""" Check Lab values of deltae against
modern ColorChecker."""
import os
import re
import argparse
from statistics import stdev
from PIL import Image
from colormath.color_objects import LabColor, AdobeRGBColor
from colormath.color_diff import delta_e_cie2000
from colormath.color_conversions import convert_color


# Coordinates of middle of color square.
# Values in percents of whole dimension - based on
# mini cc cropped to corner markings
cc_coords = {'A1': (9.94, 14.33),
             'A2': (9.94, 38.89),
             'A3': (9.94, 62.44),
             'A4': (9.94, 86.49),
             'B1': (26.05, 14.33),
             'B2': (26.05, 38.89),
             'B3': (26.05, 62.44),
             'B4': (26.05, 86.49),
             'C1': (41.81, 14.33),
             'C2': (41.81, 38.89),
             'C3': (41.81, 62.44),
             'C4': (41.81, 86.49),
             'D1': (57.92, 14.33),
             'D2': (57.92, 38.89),
             'D3': (57.92, 62.44),
             'D4': (57.92, 86.49),
             'E1': (74.02, 14.33),
             'E2': (74.02, 38.89),
             'E3': (74.02, 62.44),
             'E4': (74.02, 86.49),
             'F1': (90.47, 14.33),
             'F2': (90.47, 38.89),
             'F3': (90.47, 62.44),
             'F4': (90.47, 86.49),
             }

# Official x-rite Lab values for Colorchecker after Nov 2014
cc_after2014 = {'A1': LabColor(37.54, 14.37, 14.92),
                'A2': LabColor(62.73, 35.83, 56.5),
                'A3': LabColor(28.37, 15.42, -49.8),
                'A4': LabColor(95.19, -1.03, 2.93),
                'B1': LabColor(64.66, 19.27, 17.5),
                'B2': LabColor(39.43, 10.75, -45.17),
                'B3': LabColor(54.38, -39.72, 32.27),
                'B4': LabColor(81.29, -0.57, 0.44),
                'C1': LabColor(49.32, -3.82, -22.54),
                'C2': LabColor(50.57, 48.64, 16.67),
                'C3': LabColor(42.43, 51.05, 28.62),
                'C4': LabColor(66.89, -0.75, -0.06),
                'D1': LabColor(43.46, -12.74, 22.72),
                'D2': LabColor(30.1, 22.54, -20.87),
                'D3': LabColor(81.8, 2.67, 80.41),
                'D4': LabColor(50.76, -0.13, 0.14),
                'E1': LabColor(54.94, 9.61, -24.79),
                'E2': LabColor(71.77, -24.13, 58.19),
                'E3': LabColor(50.63, 51.28, -14.12),
                'E4': LabColor(35.63, -0.46, -0.48),
                'F1': LabColor(70.48, -32.26, -0.37),
                'F2': LabColor(71.51, 18.24, 67.37),
                'F3': LabColor(49.57, -29.71, -28.32),
                'F4': LabColor(20.64, 0.07, -0.46)}

halflist = ("A3", "A4", "B3", "B4", "C3", "C4",
            "D3", "D4", "E3", "E4", "F3", "F4")

graylist = ("A4", "B4", "C4", "D4", "E4", "F4")

text_extensions = ('.txt', '.csv')
image_extenstions = ('.png', '.jpg', '.tif')


class Patch:
    """Class to store values related to patch."""
    def __init__(self,
                 ll=None, la=None, lb=None,
                 rr=None, rg=None, rb=None,
                 px=None, py=None, de=None):
        self.ll = ll
        self.la = la
        self.lb = lb
        self.rr = rr
        self.rg = rg
        self.rb = rb
        self.px = px
        self.py = py
        self.de = de

    @property
    def x(self):
        """X coordinate of upper left corner."""
        return self.px

    @property
    def y(self):
        """Y coordinate of upper left corner."""
        return self.py

    @property
    def l(self):
        """L of Lab"""
        return self.ll

    @property
    def a(self):
        """a of Lab"""
        return self.la

    @property
    def b(self):
        """b of Lab"""
        return self.lb

    @property
    def rgb_r(self):
        """R of RGB"""
        return self.rr

    @property
    def rgb_g(self):
        """G of RGB"""
        return self.rg

    @property
    def rgb_b(self):
        """B of RGB"""
        return self.rb

    @property
    def d(self):
        """dE value for patch"""
        return self.de


def process_color_data(data_file) -> dict:
    """Create dict with fields and values in Lab
    :param data_file: name of file with data, no validation though
    :type data_file: str
    :return: dict with key: field name, value: lab values
    :rtype: dict
    """

    try:
        cc_vals = {}
        with open(data_file, encoding="utf-8") as df:
            for line in df:
                field, Lab_L, Lab_a, Lab_b = line.split()
                cc_vals[field] = LabColor(Lab_L, Lab_a, Lab_b)
    except TypeError:
        # When file not given use official values from x-rite
        cc_vals = cc_after2014.copy()

    return cc_vals


def calculate_from_text(fname: str):
    """Calculate deltae from text file in deltae.picturae format.
    :param fname: file name
    :type fname: str
    """

    try:
        with open(fname, encoding="utf-8") as f:
            patches = f.readlines()[5:29]
    except IndexError:
        raise SystemExit("something wrong with file, didn't get 24 patches.")

    if args.half:
        patches = [x for x in patches if x.startswith(halflist)]

    deglobal = []
    for line in patches:
        data = line.strip().split(',')
        # 0 - patch name, 4 - L, 5 - a, 6 - b
        point = delta_e_cie2000(cc_values[data[0]],
                                LabColor(data[4], data[5], data[6]))
        deglobal.append(point)

    # Calculate global average
    # total FADGI control requires a lot of more tests
    deltae = sum(deglobal)/len(patches)

    # Limit to 3 numbers after point, don't need 15
    print(f"dE: {deltae:.3f}")


def calculate_from_image(fname: str):
    """Calculate deltae from image file by detectinc color squares.
    :param fname: file name
    :type fname: str
    """
    cc_file = Image.open(fname)

    image_values = {}
    for patch in cc_coords:
        patch_name, patch_vals = get_patch_value(patch, cc_file)
        image_values[patch_name] = LabColor(*patch_vals)

    deglobal = []
    for patch in cc_values:
        point = delta_e_cie2000(cc_values[patch],
                                image_values[patch])

        checker_values[patch].de = point

        deglobal.append(point)

    # Calculate parameters:
    # Global dE
    deltae = sum(deglobal)/len(deglobal)
    # Tone response and White Balance
    tone, wbalance = get_tone_wb(image_values, cc_values)
    # Lightness uniformity
    light = get_ligthness_uniformity(image_values, deglobal)
    # Color accuracy
    color_acc = get_color_accuracy(deltae)

    # Limit to 3 numbers after point, don't need 15
    print(f"dE: {deltae:.3f}")
    print(f"Tone response: {tone:.3f}")
    print(f"White balance: {wbalance:.3f}")
    print(f"Lightness uniformity: {light:.3%}")
    print(f"Color accuracy: {color_acc:.3f}")

    # Create debug image
    draw_string = ""
    debug_file = ""
    for pn, pv in checker_values.items():
        # Stuff for magick drawing
        if pv.d < 4.0:
            stroke = "green"
        else:
            stroke = "red"
        draw_string += (f"-fill None -stroke {stroke} -strokewidth 2 "
                        f"-draw "
                        f"'rectangle {pv.x},{pv.y} {pv.x+100},{pv.y+100}' ")
        # Stuff for debug file
        debug_file += (f"{pn}: Lab - {pv.l:.3f}, {pv.a:.3f}, {pv.b:.3f}, "
                       f"\tRGB - {pv.rgb_r * 256:.2f}, {pv.rgb_g * 256:.2f}, "
                       f"{pv.rgb_b * 256:.2f}, "
                       f"\td2k - {pv.d:.3f}\n")

    magick_debug_string = (f"magick -quiet {re.escape(DELTAEFILE)}[0] "
                           f"{draw_string} "
                           f"{re.escape(DELTAEFILE)}_de.jpg")

    os.system(magick_debug_string)
    # Create debug file
    debug_file += (f"\n"
                   f"dE: {deltae:.3f}\n"
                   f"Tone response: {tone:.3f}\n"
                   f"White balance: {wbalance:.3f}\n"
                   f"Lightness uniformity: {light:.3%}\n"
                   f"Color accuracy: {color_acc:.3f}")

    with open("out.txt", "w", encoding="utf-8") as f:
        f.write(debug_file)


def get_tone_wb(tested: dict, reference: dict) -> tuple:
    """Get tone response for CC as defined in FADGI:
    Tone response dL2k for any given gray patch.
    :param tested: Values for patches in tested file
    :type tested: dict
    :param reference: Values for patches in reference file
    :type reference: dict
    :return: max absolute difference in gray patches in L channel
             and difference in colors
    :rtype: Tuple(float, float)
    """
    tone_response: list = []
    white_balance: list = []

    for patch_name in graylist:
        # test tone response
        test = tested[patch_name].lab_l
        ref = reference[patch_name].lab_l
        tone_response.append(abs(test - ref))
        # test white balance
        point_gray = delta_e_cie2000(tested[patch_name],
                                     reference[patch_name])
        white_balance.append(point_gray)

    return max(tone_response), max(white_balance)


def get_ligthness_uniformity(lab_values: dict, de_values: list) -> float:
    """ Get lightness uniformity - standard deviation of dE / mean L*
    :param lab_values: Values of patches
    :type lab_values: dict
    :param de_values: dE values for all patches
    :type de_values: list
    :return: Ligthness uniformity number
    :rtype: float
    """
    de_standard_deviation = stdev(de_values)
    l_values = [x.lab_l for x in lab_values.values()]
    l_mean = sum(l_values) / len(l_values)

    return de_standard_deviation / l_mean


def get_color_accuracy(de: float) -> float:
    """ Get 90th percentile color accuracy: 2.5 average deviation
    of all patches
    :param de: average deviation of all patches
    :type de: float
    :return: color accuracy
    :rtype: float
    """
    return 2.5 * de


def get_patch_value(pname, cc_file: Image):
    """ Get Lab values from single patch
    :param pname: name of patch in range of A1 - F4
    :type pname: str
    :param cc_file: Image to analyze
    :type cc_file: Image
    :return: analyzed patch name, color values, coords (upper-left)
    :rtype: str, tuple
    """
    cc_width, cc_height = cc_file.size
    # Calculate size of square to get color depending on size of
    # checker image bigger is better because we need more precise
    # approximation. Also bigger is more risk to not fit into
    # real square.
    patch_size = round(cc_width * 0.8 / 6 / 2 / 2)
    patch_size = min(patch_size, 50)
    patch_side = patch_size * 2
    # Extract middle of the patch
    cc_x = cc_coords[pname][0]
    cc_y = cc_coords[pname][1]
    # Create coords for magick extraction
    p_x = round((cc_width * cc_x / 100) - patch_size)
    p_y = round((cc_height * cc_y / 100) - patch_size)
    # Magick command:
    #   extract patch, with size of {patch_side}
    #   resize it to 1x1 to get mean color
    #   and get text for values
    magic_string = (f"magick -quiet {re.escape(cc_file.filename)}[0] "
                    f"-crop {patch_side}x{patch_side}+{p_x}+{p_y} "
                    "-resize 1x1 "
                    "-colorspace RGB "
                    "-depth 16 -colorspace sRGB txt:")
    p_text = os.popen(magic_string).read()
    # Proper way to get appropriate Lab values:
    # one pixel 0-1 values in RGB and later using colormath python:
    # Extract RGB values from magick string and convert them to 0-1 scale
    p_rgb = re.findall(r"0,0: \((.*)\) ", p_text)[0]
    rgb_full_scale = p_rgb.split(",")[:3]
    # I am dealing with 16-bit values
    rgb_r, rgb_g, rgb_b = (float(x) / 65536 for x in rgb_full_scale)

    lab_color = convert_color(AdobeRGBColor(rgb_r, rgb_g, rgb_b), LabColor,
                              target_illuminant="d50")

    lab_tuple = (lab_color.lab_l, lab_color.lab_a, lab_color.lab_b)

    checker_values[pname] = Patch(*lab_tuple,
                                  rgb_r, rgb_g, rgb_b,
                                  p_x, p_y)

    return pname, lab_tuple


if __name__ == '__main__':

    ap = argparse.ArgumentParser(description="Test color data")

    ap.add_argument("testfile", type=str,
                    help="File to test")
    ap.add_argument("--color", "-c", required=False, type=str,
                    help="L*a*b* data in file a la CTAGS")
    ap.add_argument("--coordinates", "-x", required=False, type=str,
                    help="""File with coordinates of fields in
                         percentages of file (must be in tune
                         with color data)""")
    ap.add_argument("--half", action="store_true", required=False,
                    help="""Use only lower half of checker:
                         BGRYMC, Greys (only CC family supported)""")

    args = ap.parse_args()
    cc_values = process_color_data(args.color)

    # All values for checker go here
    checker_values: dict = {}

    try:
        DELTAEFILE = args.testfile
    except IndexError:
        raise SystemExit('usage: cvs file from deltae required')

    if DELTAEFILE.endswith(text_extensions):
        calculate_from_text(DELTAEFILE)
    elif DELTAEFILE.endswith(image_extenstions):
        calculate_from_image(DELTAEFILE)
    else:
        raise SystemExit(f'usage: don\'t recognize extension of {DELTAEFILE}')
