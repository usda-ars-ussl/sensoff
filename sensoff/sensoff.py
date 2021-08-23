#!/usr/bin/env python3
"""
Corrects GPS transect coordinates when an on-the-go sensor is
significantly offset from the GPS on a mobile instrument platform.

"""
from __future__ import annotations

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
import argparse
import csv
from itertools import tee
from math import atan2, cos, hypot, isclose, pi, sin, sqrt
from typing import NamedTuple, List, Tuple, Iterable, Iterator, Any
import sys

# Standard Position Angle (SPA) == standard trigonometric unit circle
# angle having one ray coincident with the positive x-axis, positive
# in the counter-clockwise direction, and a value between (-pi, pi).

StandardPositionAngle = float
Point = Tuple[float, float]


def pairwise(s: Iterable) -> Iterator[Tuple[Any, Any]]:
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(s)
    next(b, None)
    return zip(a, b)


def headings(points: List[Point]) -> List[StandardPositionAngle]:
    """Estimate heading at each point in an OTG survey.

    The heading is computed as the average bearing of the prior and
    subsequent legs of the traverse.

    In other words, at each transect point the heading is estimated
    to be the average of the straight-line directions from and towards
    the previous and next points, respectively.
    
    The average is weighted by the lengths of the two legs, such that
    shorter legs (nearer transect points) are weighted more heavily.

    Notes
    -----
    Returns headings as standard trigonomic unit circle angles
    (value between -pi and pi, relative to positive x direction)
    rather than bearing angles (relative to positive y direction).

    """
    angles = [atan2(y1 - y0, x1 - x0) for (x0, y0), (x1, y1) in pairwise(points)]
    distances = [hypot(x1 - x0, y1 - y0) for (x0, y0), (x1, y1) in pairwise(points)]
    headings = [angles[0]]  # no weighted average for first heading

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
    headings.append(angles[-1])  # no weighted average for last heading
    return headings


class GPSCoords(List[Point]):
    """List of GPS coordinates points from OTG survey.
    
    GPSCoords = List[Point] = List[Tuple(float, float)]
    """

    @classmethod
    def from_csv(
        cls, csvfile, sep: str = ",", xcol: int = 1, ycol: int = 2, skiprows: int = 0
    ) -> GPSCoords:
        """
        csvfile : csv filename or object
            Delimited file containing GPS coordinates for OTG survey.
        xcol : int, optional
            Column in datafile with x-coordinates. Default is 1.
        ycol : int, optional
            Column in datafile with y-coordinates. Default is 2.
        sep : str, optional
            Delimiter used in coordinate datafile. Default is ",".
        skiprows : int, optional
            Number of header rows in datafile. Default is 0.

        """
        try:
            datafile = open(csvfile, newline="")
        except TypeError:
            # handle non-path-like csvfile
            # csv reader does not require a file object
            datafile = csvfile

        reader = iter(csv.reader(datafile, delimiter=sep))
        for _ in range(skiprows):
            next(reader)
        xy = []
        while True:
            try:
                row = next(reader)
                xy.append((float(row[xcol - 1]), float(row[ycol - 1])))
            except StopIteration:
                break

        try:
            datafile.close()
        except AttributeError:
            pass

        return GPSCoords(xy)

    def to_sensor_coords(
        self, inline_offset: int = 0, lateral_offset: int = 0
    ) -> List[Point]:
        """
        inline_offset : float, optional
            Sensor offset distance inline with the direction of travel.
            Positive in the direction of travel. Default is 0.
        lateral_offset : float, optional
            Sensor offset distance lateral to the direction of travel.
            Positive to the left (facing forward). Default is 0.
        """
        angles = headings(self)
        gamma = atan2(lateral_offset, inline_offset)
        radius = hypot(lateral_offset, inline_offset)
        return [
            (x + radius * cos(angle + gamma), y + radius * sin(angle + gamma))
            for (x, y), angle in zip(self, angles)
        ]


def arg_parser():
    parser = argparse.ArgumentParser(
        prog="sensoff",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=("Correct transect coordinates when sensor is offset from GPS"),
        epilog=schematic,
    )
    parser.add_argument("FILE", help="Delimited text file with GPS x,y coordinates")
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
        help="x-coordinate column (1-based) (default: %(default)d)",
    )
    parser.add_argument(
        "--ycol",
        type=int,
        default=2,
        help="y-coordinate column (1-based) (default: %(default)d)",
    )
    parser.add_argument(
        "--skiprows",
        type=int,
        help="number of datafile header rows to skip (default: %(default)s)",
    )
    parser.add_argument(
        "--sep", default=",", help="datafile delimiter (default: %(default)s)",
    )
    parser.add_argument(
        "--outfile", default=None, help="write output to file",
    )
    return parser


def main():
    parser = arg_parser()
    args = parser.parse_args()
    coords = GPSCoords.from_csv(
        csvfile=args.FILE,
        xcol=args.xcol,
        ycol=args.ycol,
        sep=args.sep,
        skiprows=args.skiprows,
    ).to_sensor_coords(inline_offset=args.ioff, lateral_offset=args.loff)

    if args.outfile is None:
        writer = csv.writer(sys.stdout, delimiter=args.sep)
        try:
            for row in coords:
                writer.writerow(row)
        except BrokenPipeError:
            pass
    else:
        with open(args.outfile, "w", newline="") as csvfile:
            writer = csv.writer(csvfile, delimiter=args.sep)
            for row in coords:
                writer.writerow(row)


if __name__ == "__main__":
    main()
