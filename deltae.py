#!/usr/bin/python
""" Check Lab values of deltae against
modern ColorChecker."""
import sys
import os
import re
from PIL import Image
from colormath.color_objects import LabColor
from colormath.color_diff import delta_e_cie2000

# Official x-rite Lab values for
# Colorchecker after Nov 2014
cc_values = {'A1': LabColor(37.54, 14.37, 14.92),
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

text_extensions = ('.txt', '.csv')
image_extenstions = ('.png', '.jpg', '.tif')


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

    deglobal = []
    for line in patches:
        data = line.strip().split(',')
        # 0 - patch name, 4 - L, 5 - a, 6 - b
        point = delta_e_cie2000(cc_values[data[0]],
                                LabColor(data[4], data[5], data[6]))
        deglobal.append(point)

    # Calculate global average
    # total FADGI control requires a lot of more tests
    deltae = sum(deglobal)/24
    # Limit to 3 numbers after point, don't need 15
    print(f"{deltae:.3f}")


def calculate_from_image(fname: str):
    """Calculate deltae from image file by detectinc color squares.
    :param fname: file name
    :type fname: str
    :return: name and values of patch
    :rtype: Tuple(Str, Tuple)
    """
    cc_file = Image.open(fname)

    image_values = dict()
    for patch in cc_coords:
        patch_name, patch_vals = get_patch_value(patch, cc_file)
        image_values[patch_name] = LabColor(*patch_vals)

    deglobal = []
    for patch in cc_values:
        point = delta_e_cie2000(cc_values[patch], image_values[patch])
        deglobal.append(point)

    # Calculate global average
    # total FADGI control requires a lot of more tests
    deltae = sum(deglobal)/24
    # Limit to 3 numbers after point, don't need 15
    print(f"{deltae:.3f}")


def get_patch_value(pname, cc_file: Image):
    """ Get Lab values from single patch """
    cc_width, cc_height = cc_file.size
    # Calculate size of square to get color depending on size of
    # checker image bigger is better because we need more precise
    # approximation. Also bigger is more risk to not fit into
    # real square.
    patch_size = cc_width * 0.8 / 6 / 2 / 2
    patch_side = patch_size * 2
    print(patch_side)
    # Extract middle of the patch
    cc_x = cc_coords[pname][0]
    cc_y = cc_coords[pname][1]
    # Create coords for magick extraction
    p_x = round((cc_width * cc_x / 100) - patch_size)
    p_y = round((cc_height * cc_y / 100) - patch_size)
    # Magick command:
    #   extract patch, with size of {patch_side}
    #   resize it to 1x1 to get mean color
    #   convert to LAB colorspace
    #   and get text for values
    magic_string = (f"magick -quiet {cc_file.filename}[0] "
                    f"-crop {patch_side}x{patch_side}+{p_x}+{p_y} "
                     "-resize 1x1 -define quantum:format=floating-point "
                     "-depth 16 -colorspace LAB txt:")
    p_text = os.popen(magic_string).read()
    # Extract LAB channel values from magick string
    p_lab = re.findall(r"cielaba?\(.*\)", p_text)[0]
    p_lab = re.sub(r"cielaba?\(", "", p_lab)
    p_lab = re.sub(r"\)", "", p_lab)
    print(pname, tuple(p_lab.split(",")[:3]))
    return pname, tuple(p_lab.split(",")[:3])


if __name__ == '__main__':

    try:
        DELTAEFILE = sys.argv[1]
    except IndexError:
        raise SystemExit('usage: cvs file from deltae required')

    if DELTAEFILE.endswith(text_extensions):
        calculate_from_text(DELTAEFILE)
    elif DELTAEFILE.endswith(image_extenstions):
        calculate_from_image(DELTAEFILE)
    else:
        raise SystemExit(f'usage: don\'t recognize extension of {DELTAEFILE}')
