import os

import numpy as np
import numpy.testing as npt
from sensoff import GPSCoords

TESTDIR = os.path.dirname(os.path.realpath(__file__))
data0 = os.path.join(TESTDIR, "dummy0.csv")
data1 = os.path.join(TESTDIR, "dummy1.csv")

csvdata_str = [
    "POINT_X,POINT_Y",
    "470533.3466,3759298.5405",
    "470533.4242,3759298.5348",
    "470533.4641,3759298.5622",
    "470533.5238,3759298.4685",
    "470533.7208,3759298.4408",
    "470533.3325,3759298.3213",
    "470533.5864,3759298.3905",
    "470533.5581,3759298.3506",
    "470533.261,3759298.1810",
]


def test_sensor_coordinates():
    ioff = 1
    loff = -1

    survey = GPSCoords.from_csv(csvdata_str, skiprows=1)
    r0 = survey.to_sensor_coords(ioff, loff)
    r1 = GPSCoords.from_csv(data0, skiprows=1).to_sensor_coords(
        inline_offset=ioff, lateral_offset=loff
    )
    r3 = GPSCoords.from_csv(data1, sep=" ", xcol=2, ycol=3, skiprows=2).to_sensor_coords(
        inline_offset=ioff, lateral_offset=loff,
    )

    r0 = np.array(r0)
    npt.assert_allclose(r0, np.array(r1))
    npt.assert_allclose(r0, np.array(r3))

    c0 = np.array(survey)
    actual_distances = np.hypot(r0[:, 0] - c0[:, 0], r0[:, 1] - c0[:, 1])[1:-1]
    desired_distance = np.hypot(loff, ioff)
    npt.assert_allclose(
        actual_distances, np.full(len(actual_distances), desired_distance)
    )


if __name__ == "__main__":
    test_sensor_coordinates()
