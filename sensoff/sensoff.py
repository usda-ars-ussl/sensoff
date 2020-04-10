#!/usr/bin/env python3
"""
Correct GPS transect coordinates when an on-the-go sensor is
significantly offset from the GPS on a mobile instrument platform.

"""
import argparse
import csv
from itertools import tee
from math import atan2, cos, hypot, isclose, pi, sin, sqrt
import sys


schematic = """
             lateral_offset

                  (+)

                   |            Direction of travel -->
             >>>>>>>>>>>>>
             >     |     >
     (-)  --->--- GPS --->---  (+) inline_offset
             >     |     >
             >>>>>>>>>>>>>
                   |
                         (mobile platform) 
                  (-)

"""


def sensor_coordinates(
    gps_file,
    inline_offset=0,
    lateral_offset=0,
    xcol=1,
    ycol=2,
    delimiter=",",
    headrows=None,
    ioff=None,
    loff=None,
):
    """Convert GPS coordinates to offset sensor coordinates.
    
    Corrects GPS coordinates when on-the-go transect data have been
    collected using a sensor that is significantly offset from the GPS
    on a mobile platform.
    
    Parameters
    ----------
    gps_file : csv filename or object
        Delimited file containing GPS coordinates for survey transect.
    inline_offset : float, optional
        Sensor offset distance inline with the direction of travel.
        Positive in the direction of travel. Default is 0.
    lateral_offset : float, optional
        Sensor offset distance lateral to the direction of travel.
        Positive to the left (facing forward). Default is 0.
    xcol : int, optional
        Column in datafile with x-coordinates. Default is 1.
    ycol : int, optional
        Column in datafile with y-coordinates. Default is 2.
    delimiter : str, optional
        Delimiter used in coordinate datafile. Default is ",".
    headrows : int, optional
        Number of header rows in datafile. Default is 0.
    ioff, loff : floats, optional
        Aliases for inline_offset and lateral_offset.

    Returns
    -------
    List of original and adjusted x,y coordinates

    """
    if ioff is None:
        ioff = inline_offset
    if loff is None:
        loff = lateral_offset

    gps_coords = read_xy(gps_file, delimiter, xcol, ycol, headrows)
    headings = platform_headings(gps_coords)
    return offset_coords(gps_coords, headings, ioff, loff)


sensor_coordinates.__doc__ += "Notes\n    -----\n" +  schematic


def read_xy(csvfile, sep=",", xcol=1, ycol=2, headrows=None):

    try:
        datafile = open(csvfile, newline="")
    except TypeError:
        # handle non-path-like csvfile
        # csv reader does not require a file object
        datafile = csvfile

    if headrows is None:
        headrows_not_passed = True
        headrows = 0
    else:
        headrows_not_passed = False
    for row in range(headrows):
        next(datafile)

    reader = iter(
        csv.reader(datafile, delimiter=sep, quoting=csv.QUOTE_NONNUMERIC)
    )
    row_cnt = 0
    rows_not_yet_read = True
    xy = []
    while True:
        row_cnt += 1
        try:
            row = next(reader)
            rows_not_yet_read = False
            xy.append((row[xcol - 1], row[ycol - 1]))
        except StopIteration:
            break
        except ValueError:
            # if errors occur within the first 5 rows, skip as if header
            if headrows_not_passed and rows_not_yet_read and row_cnt < 6:
                continue
            else:
                raise
    try:
        datafile.close()
    except AttributeError:
        pass

    return xy


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def platform_headings(gps_coords):
    """Determine platform heading at each GPS coordinate.

    The heading of the sensor platform at each GPS coordinate is
    estimated as the average bearing of the prior and subsequent legs of
    the traverse.

    In other words, at a given transect point, the platform is assumed
    to be facing a direction that is the average of the straight-line
    directions from and towards the previous and next points,
    respectively.
    
    The average is weighted by the lengths of the two legs, such that
    shorter legs (nearer transect points) are weighted more heavily.

    Returns
    -------
    list of headings given as standard position angles (not bearings)

    Notes
    -----
    Standard Position Angle (SPA) == standard trigonometric unit circle
    angle having one ray coincident with the positive x-axis, positive
    in the counter-clockwise direction, and a value between (-pi, pi).

    """
    # using SPAs in place of bearings
    angles = [
        atan2(y1 - y0, x1 - x0) for (x0, y0), (x1, y1) in pairwise(gps_coords)
    ]
    distances = [
        hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in pairwise(gps_coords)
    ]
    headings = [float("nan")]

    for (a0, a1), (d0, d1) in zip(pairwise(angles), pairwise(distances)):
        # leg angles are weighted proportional to the other leg's length
        (angle0, weight0), (angle1, weight1) = sorted([(a0, d1), (a1, d0)])

        # Split the *acute* angle formed by the terminal sides of SPAs
        # angle0 and angle1.

        if isclose(angle1 - angle0, pi):
            # no angle, rays point in opposite direction
            headings.append(float("nan"))
            continue
        if angle1 - angle0 > pi:
            angle0 += 2 * pi
        ave = (weight0 * angle0 + weight1 * angle1) / (weight0 + weight1)
        if ave > pi:
            ave -= 2 * pi
        headings.append(ave)
    headings.append(float("nan"))
    return headings


def offset_coords(gps_coords, headings, inline_offset=0, lateral_offset=0):
    "Headings must be standard trig angles"
    gamma = atan2(lateral_offset, inline_offset)
    rdist = hypot(lateral_offset, inline_offset)
    coords = [["xgps", "ygps", "xsens", "ysens"]]
    for (x, y), angle in zip(gps_coords, headings):
        xsens = x + rdist * cos(angle + gamma)
        ysens = y + rdist * sin(angle + gamma)
        coords.append([x, y, xsens, ysens])
    return coords


def arg_parser():
    parser = argparse.ArgumentParser(
        prog="sensoff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Correct transect coordinates when sensor is offset from GPS"
        ),
        epilog=schematic,
    )
    parser.add_argument(
        "FILE", help="Delimited text file with GPS x,y coordinates"
    )
    parser.add_argument(
        "--ioff",
        type=float,
        default=0,
        help=(
            "inline sensor offset, positive in direction of travel"
            " (default: %(default)d)"
        ),
    )
    parser.add_argument(
        "--loff",
        type=float,
        default=0,
        help=(
            "lateral sensor offset, positive to left (facing forward)"
            " (default: %(default)d)"
        ),
    )
    parser.add_argument(
        "--xcol",
        type=int,
        default=1,
        help="x-coordinate column (default: %(default)d)",
    )
    parser.add_argument(
        "--ycol",
        type=int,
        default=2,
        help="y-coordinate column (default: %(default)d)",
    )
    parser.add_argument(
        "--headrows",
        type=int,
        help="number of datafile header rows (default: %(default)s)",
    )
    parser.add_argument(
        "--delimiter",
        default=",",
        help="datafile delimiter (default: %(default)s)",
    )
    parser.add_argument(
        "--outfile", default=None, help="write output to file",
    )
    return parser


def main():
    parser = arg_parser()
    args = parser.parse_args()
    coords = sensor_coordinates(
        gps_file=args.FILE,
        ioff=args.ioff,
        loff=args.loff,
        xcol=args.xcol,
        ycol=args.ycol,
        delimiter=args.delimiter,
        headrows=args.headrows,
    )
    if args.outfile is None:
        writer = csv.writer(sys.stdout, delimiter=args.delimiter)
        try:
            for row in coords:
                writer.writerow(row)
        except BrokenPipeError:
            pass
    else:
        with open(args.outfile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=args.delimiter)
            for row in coords:
                writer.writerow(row)


if __name__ == "__main__":
    main()
