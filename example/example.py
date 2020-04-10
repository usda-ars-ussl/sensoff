from math import pi
import os

import numpy as np
import matplotlib.pyplot as plt

from sensoff import sensor_coordinates

EXDIR = os.path.dirname(os.path.realpath(__file__))

def gamma_example():
    outfile = os.path.join(EXDIR, "gamma_survey.png")
    print("creating", outfile, "...", end="")
    ioff = -0.5
    loff = -1.5
    datafile = os.path.join(EXDIR,"sensor_survey_GAMMA.csv")
    sc = sensor_coordinates(datafile, ioff=ioff, loff=loff)
    fig, ax = plt.subplots()
    ax = transect_plot(sc, ax)
    ax.legend(["GPS", "Sensor"])
    ax.set_title(
        f"inline offset = {ioff} m, lateral offset = {loff} m", pad=20
    )
    plt.savefig(outfile)
    print("done")


def offsets_demo():
    outfile = os.path.join(EXDIR, "offsets_demo.png")
    print("creating", outfile, "...", end="")
    # fake transect data
    xdat = np.linspace(-pi, pi)
    ydat = 6 * np.sin(xdat)
    cnt = 15
    dx = 0.2
    xdat = np.append(xdat, np.linspace(pi + dx, 7, cnt))
    ydat = np.append(ydat, np.array(cnt * [0]))
    xdat = np.append(xdat, np.array(cnt * [7]))
    ydat = np.append(ydat, np.linspace(0 + dx, 6, cnt))
    xdat = np.append(xdat, np.linspace(7 - dx, 4, cnt))
    ydat = np.append(ydat, np.array(cnt * [6]))
    xdat = np.append(xdat, np.array(cnt * [4]))
    ydat = np.append(ydat, np.linspace(6 - dx, 2, int(cnt / 2)))

    csvdata = [str(x) + "," + str(y) for x, y in zip(xdat, ydat)]
    offsets = [
        (0, 0.5),
        (0.5, 0.5),
        (0.5, 0),
        (0.5, -0.5),
        (0, -0.5),
        (-0.5, -0.5),
        (-0.5, 0),
        (-0.5, 0.5),
        (0, 0),
    ]

    fig, axes = plt.subplots(3, 3, figsize=(7, 7), sharex=True, sharey=True)
    for (ioff, loff), ax in zip(offsets, axes.flatten()):
        sensor_coords = sensor_coordinates(csvdata, ioff, loff)
        ax = transect_plot(sensor_coords, ax)
        ax.set_title(f"inline = {ioff}, lateral={loff}", fontsize=10)
        ax.axis("off")
    axes[0, 0].legend(["GPS", "Sensor"])
    axes[0, 0].text(-4, 1, "Start", fontsize=8)
    axes[0, 0].text(4.5, 1.5, "End", fontsize=8)
    fig.tight_layout()
    plt.savefig(outfile)
    print("done")


def transect_plot(coords, ax=None):
    if ax is None:
        ax = plt.gca()
    sc = np.asarray(coords[1:])
    xgps, ygps, xsens, ysens = sc[:, 0], sc[:, 1], sc[:, 2], sc[:, 3]

    ax.plot(xgps, ygps, "o", linewidth=0, markersize=1.5)
    ax.plot(xsens, ysens, "o", linewidth=0, markersize=1.5)
    for xg, yg, xs, ys in sc:
        ax.plot([xg, xs], [yg, ys], "g-", linewidth=0.5)
    ax.set_aspect("equal")
    return ax


if __name__ == "__main__":
    gamma_example()
    offsets_demo()
