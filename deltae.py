#!/usr/bin/python
""" Check Lab values of deltae against
modern ColorChecker."""
import os
import re
import argparse
from collections import namedtuple
from datetime import date
from statistics import stdev, quantiles
from typing import Any, NamedTuple
from PIL import Image
from colormath.color_objects import LabColor, AdobeRGBColor
from colormath.color_diff import delta_e_cie1976, delta_e_cie2000
from colormath.color_conversions import convert_color


# Make checker data global variable, accessible for all functions
# and imports

# Auxiliary data for repeating info about patches and checkers
# Warning this is for 05 - for test purposes just run as is
gt_colors = {"A01": LabColor(39.12, 13.24, 15.07),
             "A02": LabColor(65.43, 18.11, 18.72),
             "A03": LabColor(49.87, -4.34, -22.29),
             "A04": LabColor(44.26, -13.80, 22.85),
             "A05": LabColor(55.56, 9.82, -24.49),
             "A06": LabColor(70.82, -33.43, -0.35),
             "A07": LabColor(63.51, 34.26, 59.60),
             "A08": LabColor(39.92, 11.81, -46.07),
             "A09": LabColor(52.24, 48.55, 18.51),
             "A10": LabColor(97.06, -0.40, 1.13),
             "A11": LabColor(92.02, -0.60, 0.23),
             "A12": LabColor(83.34, -0.75, 0.21),
             "A13": LabColor(82.14, -1.06, 0.43),
             "A14": LabColor(72.06, -1.19, 0.28),
             "A15": LabColor(62.15, -1.07, 0.19),
             "A16": LabColor(49.25, -0.16, 0.01),
             "A17": LabColor(38.62, -0.18, -0.04),
             "A18": LabColor(28.86, 0.54, 0.60),
             "A19": LabColor(16.19, -0.05, 0.73),
             "A20": LabColor(8.29, -0.81, 0.19),
             "A21": LabColor(3.44, -0.23, 0.49),
             "A22": LabColor(31.41, 20.98, -19.43),
             "A23": LabColor(72.46, -24.45, 55.93),
             "A24": LabColor(72.95, 16.83, 68.80),
             "A25": LabColor(29.37, 13.06, -49.49),
             "A26": LabColor(54.91, -38.91, 30.77),
             "A27": LabColor(43.96, 52.00, 30.01),
             "A28": LabColor(82.74, 3.45, 81.29),
             "A29": LabColor(52.79, 50.88, -12.72),
             "A30": LabColor(50.87, -27.17, -29.46)}
gt_obj_lev_graylist = ("A10", "A11", "A12", "A13", "A14", "A15", "A16", "A17",
                       "A18", "A19", "A19", "A20", "A21")

checker_data = {"cc24":
                {"coords": {"A1": (9.94, 14.33),
                            "A2": (9.94, 38.89),
                            "A3": (9.94, 62.44),
                            "A4": (9.94, 86.49),
                            "B1": (26.05, 14.33),
                            "B2": (26.05, 38.89),
                            "B3": (26.05, 62.44),
                            "B4": (26.05, 86.49),
                            "C1": (41.81, 14.33),
                            "C2": (41.81, 38.89),
                            "C3": (41.81, 62.44),
                            "C4": (41.81, 86.49),
                            "D1": (57.92, 14.33),
                            "D2": (57.92, 38.89),
                            "D3": (57.92, 62.44),
                            "D4": (57.92, 86.49),
                            "E1": (74.02, 14.33),
                            "E2": (74.02, 38.89),
                            "E3": (74.02, 62.44),
                            "E4": (74.02, 86.49),
                            "F1": (90.47, 14.33),
                            "F2": (90.47, 38.89),
                            "F3": (90.47, 62.44),
                            "F4": (90.47, 86.49)},
                 "colors": {"A1": LabColor(37.54, 14.37, 14.92),
                            "A2": LabColor(62.73, 35.83, 56.5),
                            "A3": LabColor(28.37, 15.42, -49.8),
                            "A4": LabColor(95.19, -1.03, 2.93),
                            "B1": LabColor(64.66, 19.27, 17.5),
                            "B2": LabColor(39.43, 10.75, -45.17),
                            "B3": LabColor(54.38, -39.72, 32.27),
                            "B4": LabColor(81.29, -0.57, 0.44),
                            "C1": LabColor(49.32, -3.82, -22.54),
                            "C2": LabColor(50.57, 48.64, 16.67),
                            "C3": LabColor(42.43, 51.05, 28.62),
                            "C4": LabColor(66.89, -0.75, -0.06),
                            "D1": LabColor(43.46, -12.74, 22.72),
                            "D2": LabColor(30.1, 22.54, -20.87),
                            "D3": LabColor(81.8, 2.67, 80.41),
                            "D4": LabColor(50.76, -0.13, 0.14),
                            "E1": LabColor(54.94, 9.61, -24.79),
                            "E2": LabColor(71.77, -24.13, 58.19),
                            "E3": LabColor(50.63, 51.28, -14.12),
                            "E4": LabColor(35.63, -0.46, -0.48),
                            "F1": LabColor(70.48, -32.26, -0.37),
                            "F2": LabColor(71.51, 18.24, 67.37),
                            "F3": LabColor(49.57, -29.71, -28.32),
                            "F4": LabColor(20.64, 0.07, -0.46)},
                 "graylist": ("A4", "B4", "C4", "D4", "E4", "F4"),
                 "patch_fraction": 0.13
                 },
                "halfcc":
                {"coords": {"A3": (9.94, 25.00),
                            "A4": (9.94, 75.00),
                            "B3": (26.05, 25.00),
                            "B4": (26.05, 75.00),
                            "C3": (41.81, 25.00),
                            "C4": (41.81, 75.00),
                            "D3": (57.92, 25.00),
                            "D4": (57.92, 75.00),
                            "E3": (74.02, 25.00),
                            "E4": (74.02, 75.00),
                            "F3": (90.47, 25.00),
                            "F4": (90.47, 75.00)},
                 "colors": {"A3": LabColor(28.37, 15.42, -49.8),
                            "A4": LabColor(95.19, -1.03, 2.93),
                            "B3": LabColor(54.38, -39.72, 32.27),
                            "B4": LabColor(81.29, -0.57, 0.44),
                            "C3": LabColor(42.43, 51.05, 28.62),
                            "C4": LabColor(66.89, -0.75, -0.06),
                            "D3": LabColor(81.8, 2.67, 80.41),
                            "D4": LabColor(50.76, -0.13, 0.14),
                            "E3": LabColor(50.63, 51.28, -14.12),
                            "E4": LabColor(35.63, -0.46, -0.48),
                            "F3": LabColor(49.57, -29.71, -28.32),
                            "F4": LabColor(20.64, 0.07, -0.46)},
                 "graylist": ("A4", "B4", "C4", "D4", "E4", "F4"),
                 "patch_fraction": 0.13
                 },
                "nanocc":
                {"coords": {"A1": (13.8, 20.1),
                            "A2": (13.8, 39.8),
                            "A3": (13.8, 59.6),
                            "A4": (13.8, 79.6),
                            "B1": (28.5, 20.1),
                            "B2": (28.5, 39.8),
                            "B3": (28.5, 59.6),
                            "B4": (28.5, 79.6),
                            "C1": (43.0, 20.1),
                            "C2": (43.0, 39.8),
                            "C3": (43.0, 59.6),
                            "C4": (43.0, 79.6),
                            "D1": (57.7, 20.1),
                            "D2": (57.7, 39.8),
                            "D3": (57.7, 59.6),
                            "D4": (57.7, 79.6),
                            "E1": (72.3, 20.1),
                            "E2": (72.3, 39.8),
                            "E3": (72.3, 59.6),
                            "E4": (72.3, 79.6),
                            "F1": (86.8, 20.1),
                            "F2": (86.8, 39.8),
                            "F3": (86.8, 59.6),
                            "F4": (86.8, 79.6)},
                 "colors": {"A1": LabColor(37.54, 14.37, 14.92),
                            "A2": LabColor(62.73, 35.83, 56.5),
                            "A3": LabColor(28.37, 15.42, -49.8),
                            "A4": LabColor(95.19, -1.03, 2.93),
                            "B1": LabColor(64.66, 19.27, 17.5),
                            "B2": LabColor(39.43, 10.75, -45.17),
                            "B3": LabColor(54.38, -39.72, 32.27),
                            "B4": LabColor(81.29, -0.57, 0.44),
                            "C1": LabColor(49.32, -3.82, -22.54),
                            "C2": LabColor(50.57, 48.64, 16.67),
                            "C3": LabColor(42.43, 51.05, 28.62),
                            "C4": LabColor(66.89, -0.75, -0.06),
                            "D1": LabColor(43.46, -12.74, 22.72),
                            "D2": LabColor(30.1, 22.54, -20.87),
                            "D3": LabColor(81.8, 2.67, 80.41),
                            "D4": LabColor(50.76, -0.13, 0.14),
                            "E1": LabColor(54.94, 9.61, -24.79),
                            "E2": LabColor(71.77, -24.13, 58.19),
                            "E3": LabColor(50.63, 51.28, -14.12),
                            "E4": LabColor(35.63, -0.46, -0.48),
                            "F1": LabColor(70.48, -32.26, -0.37),
                            "F2": LabColor(71.51, 18.24, 67.37),
                            "F3": LabColor(49.57, -29.71, -28.32),
                            "F4": LabColor(20.64, 0.07, -0.46)},
                 "graylist": ("A4", "B4", "C4", "D4", "E4", "F4"),
                 "patch_fraction": 0.07
                 },
                "halfnanocc":
                {"coords": {"A3": (13.8, 24.0),
                            "A4": (13.8, 74.0),
                            "B3": (28.5, 24.0),
                            "B4": (28.5, 74.0),
                            "C3": (43.0, 24.0),
                            "C4": (43.0, 74.0),
                            "D3": (57.7, 24.0),
                            "D4": (57.7, 74.0),
                            "E3": (72.3, 24.0),
                            "E4": (72.3, 74.0),
                            "F3": (86.8, 24.0),
                            "F4": (86.8, 74.0)},
                 "colors": {"A3": LabColor(28.37, 15.42, -49.8),
                            "A4": LabColor(95.19, -1.03, 2.93),
                            "B3": LabColor(54.38, -39.72, 32.27),
                            "B4": LabColor(81.29, -0.57, 0.44),
                            "C3": LabColor(42.43, 51.05, 28.62),
                            "C4": LabColor(66.89, -0.75, -0.06),
                            "D3": LabColor(81.8, 2.67, 80.41),
                            "D4": LabColor(50.76, -0.13, 0.14),
                            "E3": LabColor(50.63, 51.28, -14.12),
                            "E4": LabColor(35.63, -0.46, -0.48),
                            "F3": LabColor(49.57, -29.71, -28.32),
                            "F4": LabColor(20.64, 0.07, -0.46)},
                 "graylist": ("A4", "B4", "C4", "D4", "E4", "F4"),
                 "patch_fraction": 0.07
                 },
                "gtdl":
                {"coords": {"A01": (33.6, 25.00),
                            "A02": (38.0, 25.00),
                            "A03": (42.2, 25.00),
                            "A04": (46.2, 25.00),
                            "A05": (50.5, 25.00),
                            "A06": (54.6, 25.00),
                            "A07": (58.7, 25.00),
                            "A08": (63.0, 25.00),
                            "A09": (66.8, 25.00),
                            "A10": (39.9, 32.1),
                            "A11": (44.0, 32.1),
                            "A12": (48.1, 32.1),
                            "A13": (52.2, 32.1),
                            "A14": (56.4, 32.1),
                            "A15": (60.5, 32.1),
                            "A16": (39.9, 63.9),
                            "A17": (44.0, 63.9),
                            "A18": (48.1, 63.9),
                            "A19": (52.2, 63.9),
                            "A20": (56.4, 63.9),
                            "A21": (60.5, 63.9),
                            "A22": (33.6, 71.2),
                            "A23": (38.0, 71.2),
                            "A24": (42.2, 71.2),
                            "A25": (46.2, 71.2),
                            "A26": (50.5, 71.2),
                            "A27": (54.6, 71.2),
                            "A28": (58.7, 71.2),
                            "A29": (63.0, 71.2),
                            "A30": (66.8, 71.2)},
                 "colors": {"A01": LabColor(39.12, 13.24, 15.07),
                            "A02": LabColor(65.43, 18.11, 18.72),
                            "A03": LabColor(49.87, -4.34, -22.29),
                            "A04": LabColor(44.26, -13.80, 22.85),
                            "A05": LabColor(55.56, 9.82, -24.49),
                            "A06": LabColor(70.82, -33.43, -0.35),
                            "A07": LabColor(63.51, 34.26, 59.60),
                            "A08": LabColor(39.92, 11.81, -46.07),
                            "A09": LabColor(52.24, 48.55, 18.51),
                            "A10": LabColor(97.06, -0.40, 1.13),
                            "A11": LabColor(92.02, -0.60, 0.23),
                            "A12": LabColor(83.34, -0.75, 0.21),
                            "A13": LabColor(82.14, -1.06, 0.43),
                            "A14": LabColor(72.06, -1.19, 0.28),
                            "A15": LabColor(62.15, -1.07, 0.19),
                            "A16": LabColor(49.25, -0.16, 0.01),
                            "A17": LabColor(38.62, -0.18, -0.04),
                            "A18": LabColor(28.86, 0.54, 0.60),
                            "A19": LabColor(16.19, -0.05, 0.73),
                            "A20": LabColor(8.29, -0.81, 0.19),
                            "A21": LabColor(3.44, -0.23, 0.49),
                            "A22": LabColor(31.41, 20.98, -19.43),
                            "A23": LabColor(72.46, -24.45, 55.93),
                            "A24": LabColor(72.95, 16.83, 68.80),
                            "A25": LabColor(29.37, 13.06, -49.49),
                            "A26": LabColor(54.91, -38.91, 30.77),
                            "A27": LabColor(43.96, 52.00, 30.01),
                            "A28": LabColor(82.74, 3.45, 81.29),
                            "A29": LabColor(52.79, 50.88, -12.72),
                            "A30": LabColor(50.87, -27.17, -29.46)},
                 "graylist": gt_obj_lev_graylist,
                 "patch_fraction": 0.026
                 },
                "gt20":
                {"coords": {'A01': (5.00, 39.7),
                            'A02': (7.8, 39.7),
                            'A03': (10.6, 39.7),
                            'A04': (13.2, 39.7),
                            'A05': (15.9, 39.7),
                            'A06': (18.6, 39.7),
                            'A07': (21.5, 39.7),
                            'A08': (24.1, 39.7),
                            'A09': (26.8, 39.7),
                            'A10': (29.7, 39.7),
                            'A11': (32.3, 39.7),
                            'A12': (35.0, 39.7),
                            'A13': (37.7, 39.7),
                            'A14': (40.5, 39.7),
                            'A15': (43.3, 39.7),
                            'A16': (56.9, 39.7),
                            'A17': (59.6, 39.7),
                            'A18': (62.3, 39.7),
                            'A19': (65.1, 39.7),
                            'A20': (67.9, 39.7),
                            'A21': (70.6, 39.7),
                            'A22': (73.3, 39.7),
                            'A23': (76.0, 39.7),
                            'A24': (78.9, 39.7),
                            'A25': (81.5, 39.7),
                            'A26': (84.2, 39.7),
                            'A27': (87.0, 39.7),
                            'A28': (89.7, 39.7),
                            'A29': (92.5, 39.7),
                            'A30': (95.2, 39.7)},
                 "colors": {"A01": LabColor(38.76, 13.81, 14.69),
                            "A02": LabColor(65.15, 19.21, 17.92),
                            "A03": LabColor(49.61, -4.20, -21.33),
                            "A04": LabColor(43.54, -12.89, 22.66),
                            "A05": LabColor(55.52, 8.78, -24.31),
                            "A06": LabColor(70.42, -32.39, -0.48),
                            "A07": LabColor(63.13, 35.43, 57.84),
                            "A08": LabColor(40.08, 10.25, -44.77),
                            "A09": LabColor(51.75, 47.36, 16.93),
                            "A10": LabColor(95.34, -0.90, 1.90),
                            "A11": LabColor(92.09, -0.92, 1.46),
                            "A12": LabColor(86.92, -1.12, 0.97),
                            "A13": LabColor(82.37, -1.12, 0.56),
                            "A14": LabColor(72.17, -1.05, -0.04),
                            "A15": LabColor(62.32, -1.1, -0.01),
                            "A16": LabColor(49.61, -1.29, -0.1),
                            "A17": LabColor(38.89, -0.23, -0.48),
                            "A18": LabColor(28.6, -1.09, 0.07),
                            "A19": LabColor(17.97, 0.04, 0.09),
                            "A20": LabColor(9.50, 0.45, 0.25),
                            "A21": LabColor(4.33, 0.32, -0.47),
                            "A22": LabColor(30.32, 22.13, -19.02),
                            "A23": LabColor(72.5, -22.92, 56.08),
                            "A24": LabColor(72.10, 19.51, 67.85),
                            "A25": LabColor(29.51, 13.42, -47.69),
                            "A26": LabColor(55.60, -38.46, 32.19),
                            "A27": LabColor(43.48, 50.74, 29.13),
                            "A28": LabColor(82.02, 3.28, 78.75),
                            "A29": LabColor(52.85, 49.90, -12.86),
                            "A30": LabColor(50.86, -27.78, -27.68)},
                 "graylist": gt_obj_lev_graylist,
                 "patch_fraction": 0.026
                 },
                "gt10":
                {"coords": {"A01": (5.00, 37.00),
                            "A02": (7.8, 37.00),
                            "A03": (10.6, 37.00),
                            "A04": (13.3, 37.00),
                            "A05": (16.0, 37.00),
                            "A06": (18.6, 37.00),
                            "A07": (21.5, 37.00),
                            "A08": (24.1, 37.00),
                            "A09": (26.8, 37.00),
                            "A10": (29.5, 37.00),
                            "A11": (32.3, 37.00),
                            "A12": (35.0, 37.00),
                            "A13": (37.7, 37.00),
                            "A14": (40.4, 37.00),
                            "A15": (43.2, 37.00),
                            "A16": (56.9, 37.00),
                            "A17": (59.6, 37.00),
                            "A18": (62.3, 37.00),
                            "A19": (65.1, 37.00),
                            "A20": (67.8, 37.00),
                            "A21": (70.4, 37.00),
                            "A22": (73.2, 37.00),
                            "A23": (76.0, 37.00),
                            "A24": (78.7, 37.00),
                            "A25": (81.4, 37.00),
                            "A26": (84.1, 37.00),
                            "A27": (86.8, 37.00),
                            "A28": (89.6, 37.00),
                            "A29": (92.3, 37.00),
                            "A30": (95.0, 37.00)},
                 "colors": {"A01": LabColor(38.76, 13.81, 14.69),
                            "A02": LabColor(65.15, 19.21, 17.92),
                            "A03": LabColor(49.61, -4.20, -21.33),
                            "A04": LabColor(43.54, -12.89, 22.66),
                            "A05": LabColor(55.52, 8.78, -24.31),
                            "A06": LabColor(70.42, -32.39, -0.48),
                            "A07": LabColor(63.13, 35.43, 57.84),
                            "A08": LabColor(40.08, 10.25, -44.77),
                            "A09": LabColor(51.75, 47.36, 16.93),
                            "A10": LabColor(95.34, -0.90, 1.90),
                            "A11": LabColor(92.09, -0.92, 1.46),
                            "A12": LabColor(86.92, -1.12, 0.97),
                            "A13": LabColor(82.37, -1.12, 0.56),
                            "A14": LabColor(72.17, -1.05, -0.04),
                            "A15": LabColor(62.32, -1.1, -0.01),
                            "A16": LabColor(49.61, -1.29, -0.1),
                            "A17": LabColor(38.89, -0.23, -0.48),
                            "A18": LabColor(28.6, -1.09, 0.07),
                            "A19": LabColor(17.97, 0.04, 0.09),
                            "A20": LabColor(9.50, 0.45, 0.25),
                            "A21": LabColor(4.33, 0.32, -0.47),
                            "A22": LabColor(30.32, 22.13, -19.02),
                            "A23": LabColor(72.5, -22.92, 56.08),
                            "A24": LabColor(72.10, 19.51, 67.85),
                            "A25": LabColor(29.51, 13.42, -47.69),
                            "A26": LabColor(55.60, -38.46, 32.19),
                            "A27": LabColor(43.48, 50.74, 29.13),
                            "A28": LabColor(82.02, 3.28, 78.75),
                            "A29": LabColor(52.85, 49.90, -12.86),
                            "A30": LabColor(50.86, -27.78, -27.68)},
                 "graylist": gt_obj_lev_graylist,
                 "patch_fraction": 0.026
                 },
                "gt05":
                {"coords": {"A01": (5.10, 37.00),
                            "A02": (8.0, 37.00),
                            "A03": (10.6, 37.00),
                            "A04": (13.1, 37.00),
                            "A05": (16.0, 37.00),
                            "A06": (18.6, 37.00),
                            "A07": (21.4, 37.00),
                            "A08": (24.1, 37.00),
                            "A09": (26.9, 37.00),
                            "A10": (29.5, 37.00),
                            "A11": (32.3, 37.00),
                            "A12": (35.0, 37.00),
                            "A13": (37.7, 37.00),
                            "A14": (40.4, 37.00),
                            "A15": (43.2, 37.00),
                            "A16": (57.2, 37.00),
                            "A17": (59.8, 37.00),
                            "A18": (62.5, 37.00),
                            "A19": (65.2, 37.00),
                            "A20": (68.1, 37.00),
                            "A21": (70.8, 37.00),
                            "A22": (73.4, 37.00),
                            "A23": (76.2, 37.00),
                            "A24": (79.0, 37.00),
                            "A25": (81.8, 37.00),
                            "A26": (84.5, 37.00),
                            "A27": (87.2, 37.00),
                            "A28": (89.9, 37.00),
                            "A29": (92.7, 37.00),
                            "A30": (95.3, 37.00)},
                 "colors": {"A01": LabColor(39.12, 13.24, 15.07),
                            "A02": LabColor(65.43, 18.11, 18.72),
                            "A03": LabColor(49.87, -4.34, -22.29),
                            "A04": LabColor(44.26, -13.80, 22.85),
                            "A05": LabColor(55.56, 9.82, -24.49),
                            "A06": LabColor(70.82, -33.43, -0.35),
                            "A07": LabColor(63.51, 34.26, 59.60),
                            "A08": LabColor(39.92, 11.81, -46.07),
                            "A09": LabColor(52.24, 48.55, 18.51),
                            "A10": LabColor(97.06, -0.40, 1.13),
                            "A11": LabColor(92.02, -0.60, 0.23),
                            "A12": LabColor(83.34, -0.75, 0.21),
                            "A13": LabColor(82.14, -1.06, 0.43),
                            "A14": LabColor(72.06, -1.19, 0.28),
                            "A15": LabColor(62.15, -1.07, 0.19),
                            "A16": LabColor(49.25, -0.16, 0.01),
                            "A17": LabColor(38.62, -0.18, -0.04),
                            "A18": LabColor(28.86, 0.54, 0.60),
                            "A19": LabColor(16.19, -0.05, 0.73),
                            "A20": LabColor(8.29, -0.81, 0.19),
                            "A21": LabColor(3.44, -0.23, 0.49),
                            "A22": LabColor(31.41, 20.98, -19.43),
                            "A23": LabColor(72.46, -24.45, 55.93),
                            "A24": LabColor(72.95, 16.83, 68.80),
                            "A25": LabColor(29.37, 13.06, -49.49),
                            "A26": LabColor(54.91, -38.91, 30.77),
                            "A27": LabColor(43.96, 52.00, 30.01),
                            "A28": LabColor(82.74, 3.45, 81.29),
                            "A29": LabColor(52.79, 50.88, -12.72),
                            "A30": LabColor(50.87, -27.17, -29.46)},
                 "graylist": gt_obj_lev_graylist,
                 "patch_fraction": 0.026
                 }
                }

text_extensions = ('.txt', '.csv')
image_extensions = ('.png', '.jpg', '.tif')


class Patch:
    """Class to store values related to patch."""
    def __init__(self,
                 ll=None, la=None, lb=None,
                 rr=None, rg=None, rb=None,
                 px=None, py=None, ps=None,
                 de=None):
        self.ll = ll
        self.la = la
        self.lb = lb
        self.rr = rr
        self.rg = rg
        self.rb = rb
        self.px = px
        self.py = py
        self.ps = ps
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

    @property
    def size(self):
        """Size of probe"""
        return self.ps


# Coordinates of middle of color square.
# Values in percents of whole dimension - based on
# mini cc cropped to corner markings
def load_checker_data(checker_name="cc24") -> tuple:
    """Load checker data
    :param checker_name: name of checker to get data for
    :type checker_name: str
    :return: return data related to checker:
             color and patch coords, patch fraction size
    :rtype: tuple

    Should be class?
    """

    check_colors = checker_data[checker_name]["colors"]
    check_coords = checker_data[checker_name]["coords"]
    check_gray = checker_data[checker_name]["graylist"]
    check_fraction = checker_data[checker_name]["patch_fraction"]

    return check_colors, check_coords, check_gray, check_fraction


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
        cc_vals = cc_colors.copy()

    return cc_vals


def delta_e_calc(color1, color2) -> float:
    """Return values of deltaE depending on CLI option.
    Available options are 2k (dE 2000) and 76 (dE 1976)
    :param color1: first color
    :type color1: iterable
    :param color2: second color
    :type color2: iterable
    :return: calculated deltaE value
    :rtype: float
    """
    calculated_delta_e = "100.0"

    if args.deltae == "2k":
        calculated_delta_e = delta_e_cie2000(color1, color2)
    elif args.deltae == "76":
        calculated_delta_e = delta_e_cie1976(color1, color2)

    return calculated_delta_e


def calculate_from_text(fname: str):
    """Calculate deltae from text file in deltae.picturae format.
    :param fname: file name
    :type fname: str
    """

    try:
        with open(fname, encoding="utf-8") as f:
            patches = f.readlines()[5:29]
    except IndexError as ecft:
        raise SystemExit("something wrong with file, "
                         "didn't get 24 patches.") from ecft

    deglobal = []
    for line in patches:
        data = line.strip().split(',')
        # 0 - patch name, 4 - L, 5 - a, 6 - b
        point = delta_e_calc(cc_values[data[0]],
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
        point = delta_e_calc(cc_values[patch], image_values[patch])

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
    color_acc = get_color_accuracy(deglobal)

    # Create string with exif data
    exif_data = get_exif_data(cc_file.filename)
    exif_fadgi_str = create_exif_string(exif_data,
                                        deltae,
                                        tone,
                                        wbalance,
                                        light,
                                        color_acc)

    # Limit to 3 numbers after point, don't need 15
    term_string = f"{exif_fadgi_str}"

    # Initialize ImageMagick command
    draw_string = ""
    # Initialize debug file content
    debug_file = ""
    for pn, pv in checker_values.items():
        # Stuff for magick drawing
        # Marker becomes red when dE bigger than 3.0 which means
        # it falls below 3* in FADGI2023
        if pv.d <= 3.5:
            stroke = "green"
        else:
            stroke = "red"
        psize = checker_values[patch].size
        # pointsize parametric or rescale everything for same size
        draw_string += (f"-fill None -stroke {stroke} -strokewidth 2 "
                        f"-draw "
                        f"'rectangle {pv.x},{pv.y} "
                        f"{pv.x+psize},{pv.y+psize}' "
                        f"-font Consolas -pointsize 30 "
                        f"-fill white -stroke black -strokewidth 1 "
                        f"-draw "
                        f"'text {pv.x},{pv.y+psize+30} \"{pv.d:.2f}\"' "
                        )
        # Stuff for debug file
        debug_file += (f"{pn}: Lab - {pv.l:.3f}, {pv.a:.3f}, {pv.b:.3f}, "
                       f"\tRGB - {pv.rgb_r * 256:.2f}, {pv.rgb_g * 256:.2f}, "
                       f"{pv.rgb_b * 256:.2f}, "
                       f"\tdE2k - {pv.d:.3f}\n")

    # Get list of properties about file and add them to file
    term_string = (f"{term_string}\n"
                   f"{date.isoformat(date.today())}, "
                   "deltae.py, Mikołaj Machowski 2024")
    draw_string += (f"-background white "
                    f"-fill black "
                    f"-font Consolas -pointsize 40 "
                    f"label:'{term_string}' -append "
                    )

    # Create debug file
    debug_file += (f"\n{term_string}")

    magick_debug_string = (f"magick -quiet {re.escape(DELTAEFILE)}[0] "
                           f"-rotate {cc_rotation} "
                           f"{draw_string} "
                           f"{re.escape(DELTAEFILE)}_de.jpg")

    os.system(magick_debug_string)

    with open(f"{fname}.txt", "w", encoding="utf-8") as f:
        f.write(debug_file)


def get_exif_data(fname) -> tuple:
    """Get exif data for file and return it structured
    :param fname: Name of file
    :type fname: str
    :return: Named tuple with structured data for exif
    :rtype: NamedTuple
    """
    exif_out = os.popen("exiftool -s -S -T "
                        "-Filename "
                        "-FileType "
                        "-Creator "
                        "-ColorMode "
                        "-XResolution "
                        "-Make "
                        "-Model "
                        "-SerialNumber "
                        "-Lens "
                        "-ProfileDescription "
                        "-BitsPerSample "
                        "-ShutterSpeed "
                        "-Aperture "
                        "-ISO "
                        "-Compression "
                        f"{re.escape(fname)}").read().split("\t")

    Edata = namedtuple('Edata',
                       ['filename', 'filetype', 'creator', 'colormode',
                        'resolution', 'make', 'model', 'serialnumber',
                        'lens', 'profile', 'bps',
                        'shutter', 'aperture', 'iso'])

    # Remove last element, we get it only to scrap and get rid of new line
    # added by Windows version of exiftool
    exifd = Edata._make(exif_out[:-1])

    return exifd


def create_exif_string(ex_data, de, tone, wb, lu, ca) -> str:
    """Create string with exif data for debug files
    It will consists of two parts. General metadata and FADGI
    :param exifdata: Exif data in namedtuple
    :type exifdata: namedtuple
    :param de: deltaE 2000
    :type de: float
    :param tone: tone
    :type tone: float
    :param wb: white balance
    :type tone: float
    :param lu: Light uniformity
    :type tone: float
    :param ca: Color accuracy
    :type tone: float
    :return: string to add for jpg and text files
    :rtype: str
    """

    serial_no = ""
    if ex_data.serialnumber != "-":
        serial_no = f" ({ex_data.serialnumber})"

    general_txt = (f"{'Filename:':9} {ex_data.filename}\n"
                   f"{'Author:':9} {ex_data.creator}\n"
                   f"{'Camera:':9} {ex_data.make} {ex_data.model}{serial_no}\n"
                   f"{'Lens:':9} {ex_data.lens}\n"
                   f"{'ISO:':9} {ex_data.iso:9} "
                   f"{'Aperture:':9} {ex_data.aperture:9} "
                   f"{'Shutter:':9} {ex_data.shutter:9}")

    fadgi_data = (de, ex_data.filetype, ex_data.bps, ex_data.profile,
                  ex_data.colormode, tone, wb, lu, ca)

    fadgi_stars = get_stars(fadgi_data)

    det_txt = ""

    if args.deltae == "2k":

        det_txt = ("FADGI2023: prints, photographs, "
                   "maps, posters, paintings, other 2D art\n\n"
                   f"{'DeltaE 2000:':23}{fadgi_stars.de}{de:.3f}\n"
                   f"{'Filetype:':23}{fadgi_stars.ft}{ex_data.filetype}\n"
                   f"{'Bit depth:':23}{fadgi_stars.bd}{ex_data.bps}\n"
                   f"{'Color profile:':23}{fadgi_stars.icc}{ex_data.profile}\n"
                   f"{'Color mode:':23}{fadgi_stars.cm}{ex_data.colormode}\n"
                   f"{'Tone response:':23}{fadgi_stars.tone}{tone:.3f}\n"
                   f"{'White balance:':23}{fadgi_stars.wb}{wb:.3f}\n"
                   f"{'Lightness uniformity:':23}{fadgi_stars.lu}{lu:.3%}\n"
                   f"{'Color accuracy:':23}{fadgi_stars.ca}{ca:.3f}\n"
                   )

    elif args.deltae == "76":

        det_txt = ("Metamorfoze: preserving the paper heritage\n\n"
                   f"{'DeltaE 1976:':23}{de:.3f}\n"
                   f"{'Filetype:':23}{ex_data.filetype}\n"
                   f"{'Bit depth:':23}{ex_data.bps}\n"
                   f"{'Color profile:':23}{ex_data.profile}\n"
                   f"{'Color mode:':23}{ex_data.colormode}\n"
                   )

    return general_txt + "\n\n" + det_txt


def get_stars(color_data: tuple) -> NamedTuple:
    """Process parameters of color and return star rating according
    to FADGI 2023
    :param color_data: color data
    :type color_data: tuple
    :return: named tuple of strings
    :rtype: namedtuple

    FADGI 2023
    Prints and photographs,
    Bound volumes: rare and special materials
    Documents (unbound): manuscripts and other rare and special materials
    Documents (unbound): general collections
    Oversize items: maps, posters and other materials
    Paintings and other 2D art

    File Format
    1-4 stars TIFF, JP2 (JPEG 2000)
    Bit depth
    1-2 stars 8 bit
    3-4 stars 16 bit
    Color space
    1-2 sRGB
    3-4 Adobe RGB (1998), ProPhoto, ECIRGB_v2
    Color Mode
    1 Grayscale
    2-4 Color (RGB)
    Tone Response
    1 <= 6, 2 <= 4.5, 3 <= 3, 4 <= 1.5
    White balance
    1 <= 8, 2 <= 6, 3 <= 4, 4 <= 2
    Lightness uniformity
    1 <= 8%, 2 <= 5%, 3 <= 3%, 4 <= 1%
    DeltaE 2k
    1 <= 6.5, 2 <= 5, 3 <= 3.5, 4 <= 2
    Color accuracy
    1 <= 13, 2 <= 10, 3 <= 7, 4 <= 4
    Color channel Misregistration (unimplemented)
    1 <= 1.2, 2 <= 0.8, 3 <= 0.5, 4 <= 0.33
    SFR10 (unimplemented)
    1 >= 60%, 2 >= 70%, 3 >= 80%, 4 >= 90%
    SFR50 (unimplemented)
    ---
    Sharpening (units max modulation) (unimplemented)
    1 < 1.15, 2 < 1.1, 3 < 1.05, 4 <= 1.02
    Noise (Upper limit, Units Std Dev of L*) (unimplemented)
    1 <= 4, 2 <= 3, 3 <= 2, 4 <= 1


    """
    deltae, ftype, bdepth, icc, cmode, toner, whiteb, lunif, cacc = color_data

    init_data: list[Any] = []

    # Deltae test
    if deltae <= 2:
        init_data.append(4)
    elif deltae <= 3.5:
        init_data.append(3)
    elif deltae <= 5:
        init_data.append(2)
    elif deltae <= 6.5:
        init_data.append(1)
    else:
        init_data.append("No stars!")

    # Filetype test
    if ftype in ["TIFF", "JP2"]:
        init_data.append(4)
    else:
        init_data.append("-")

    # Bitdepth test
    if bdepth in ("16 16 16", "16"):
        init_data.append(4)
    elif bdepth in ("8 8 8", "8"):
        init_data.append(2)
    else:
        init_data.append("Unknown bit-depth")

    # ICC test
    if icc in ["Adobe RGB (1998)", "ProPhoto", "ECIRGB_v2"]:
        init_data.append(4)
    elif icc == "sRGB":
        init_data.append(2)
    else:
        init_data.append(f"Unknown profile ({icc})")

    # Color mode test
    if cmode == "RGB":
        init_data.append(4)
    else:
        init_data.append(f"{cmode}")

    # Tone response test
    if toner <= 1.5:
        init_data.append(4)
    elif toner <= 3:
        init_data.append(3)
    elif toner <= 4.5:
        init_data.append(2)
    elif toner <= 6:
        init_data.append(1)
    else:
        init_data.append("-")

    # White balance test
    if whiteb <= 2:
        init_data.append(4)
    elif whiteb <= 4:
        init_data.append(3)
    elif whiteb <= 6:
        init_data.append(2)
    elif whiteb <= 8:
        init_data.append(1)
    else:
        init_data.append("-")

    # Lightness uniformity test
    if lunif <= 1:
        init_data.append(4)
    elif lunif <= 3:
        init_data.append(3)
    elif lunif <= 5:
        init_data.append(2)
    elif lunif <= 6.5:
        init_data.append(1)
    else:
        init_data.append("-")

    # Color accuracy test
    if cacc <= 4:
        init_data.append(4)
    elif cacc <= 7:
        init_data.append(3)
    elif cacc <= 10:
        init_data.append(2)
    elif cacc <= 13:
        init_data.append(1)
    else:
        init_data.append("-")

    # STAR = "★"   # ALT+9733
    STAR = "*"
    final_stars = [f"{x * STAR:10}"
                   if isinstance(x, int) else f"{x:10}" for x in init_data]

    Stars = namedtuple('Stars', 'de, ft, bd, icc, cm, tone, wb, lu, ca')

    fadgi = Stars._make(final_stars)

    return fadgi


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

    for patch_name in cc_graylist:
        # test tone response
        test = tested[patch_name].lab_l
        ref = reference[patch_name].lab_l
        tone_response.append(abs(test - ref))
        # test white balance
        point_gray = delta_e_calc(tested[patch_name], reference[patch_name])
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


def get_color_accuracy(de: list) -> float:
    """ Get 90th percentile color accuracy of all patches
    :param de: list of deltae of all patches
    :type de: list
    :return: color accuracy
    :rtype: float
    """
    color_accuracy = quantiles(de, n=10)[-1]
    return color_accuracy


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

    # We have to 'rotate' values to get proper patch positions for
    # W (270), E (90) positions
    if cc_rotation in (270, 90):
        cc_height, cc_width = cc_width, cc_height

    # Calculate size of square to get color depending on size of
    # checker image bigger is better because we need more precise
    # approximation. Also bigger is more risk to not fit into
    # real square.
    patch_size = round(cc_width * cc_ps / 2)
    patch_size = min(patch_size, 25)
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
                    f"-rotate {cc_rotation} "
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
                                  p_x, p_y,
                                  patch_side)

    return pname, lab_tuple


if __name__ == '__main__':

    ap = argparse.ArgumentParser(description="Test color data")

    ap.add_argument("testfile", type=str,
                    help="File to test")
    ap.add_argument("--checker", "-c",
                    nargs="?", default="cc24", choices=[*checker_data.keys()],
                    help="""Name of checker, supported values:
                         - c24 (classic and mini) - default,
                         - halfcc (lower half of them - grays and BGRYMC),
                         - nanocc (nano version of classic CC),
                         - halfnanocc (lower half - grays and BGRYMC),
                         - gtdl (GoldenThread Device Level),
                         - gt20 (GoldenThread Big),
                         - gt10 (GoldenThread Regular),
                         - gt05 (GoldenThread Small)""")
    ap.add_argument("--orientation", "-o",
                    nargs="?", default="S", choices=['S', 'W', 'N', 'E'],
                    help="""Orientation of checker:
                         possible values are S, W, N, E (default S)
                         S - in case of CC family greys are at the bottom,
                             in case of GT you can read text normally,
                         W - greys are on the left,
                         N - greys are on the top,
                         E - greys are on the left""")
    ap.add_argument("--deltae", "-d", type=str,
                    nargs="?", default="2k", choices=['2k', '76'],
                    help="""DeltaE difference according to:
                         - 2k (default) deltaE 2000 (ass. with FADGI)
                         - 76 deltaE 1976 (ass. with Metamorfoze)""")
    ap.add_argument("--color", required=False, type=str,
                    help="L*a*b* data in file a la CTAGS")
    ap.add_argument("--coordinates", "-x", required=False, type=str,
                    help="""File with coordinates of fields in
                         percentages of file (must be in tune
                         with color data)""")

    args = ap.parse_args()

    # All values for checker go here
    checker_values: dict = {}

    # Rotate checker to make sure we have it in proper orientation
    # With S - everythin is OK, with W bottom is on the left and we have
    # to rotate it 270 degrees, with N bottom is on top, etc.
    cc_rotation_values = {'S': 0, 'W': 270, 'N': 180, 'E': 90}
    cc_rotation = cc_rotation_values[args.orientation]

    # Get data for particular color checker
    cc_colors, cc_coords, cc_graylist, cc_ps = load_checker_data(args.checker)
    cc_name = args.checker

    # Fill color data
    cc_values = process_color_data(args.color)

    try:
        DELTAEFILE = args.testfile
    except IndexError as ede:
        raise SystemExit('usage: cvs file from deltae required') from ede

    if DELTAEFILE.endswith(text_extensions):
        calculate_from_text(DELTAEFILE)
    elif DELTAEFILE.endswith(image_extensions):
        calculate_from_image(DELTAEFILE)
    else:
        raise SystemExit(f'usage: don\'t recognize extension of {DELTAEFILE}')
