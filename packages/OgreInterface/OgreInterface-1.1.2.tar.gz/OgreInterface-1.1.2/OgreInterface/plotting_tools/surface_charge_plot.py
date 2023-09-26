from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from OgreInterface.generate import SurfaceGenerator
# from OgreInterface.generate import InterfaceGenerator, SurfaceGenerator
# from OgreInterface.surfaces import Surface
# from OgreInterface.surface_match import IonicSurfaceMatcher
# from OgreInterface import utils
# from pymatgen.core.structure import Structure
# from pymatgen.io.vasp.inputs import Poscar
# from pymatgen.core.periodic_table import Element
# from pymatgen.analysis.local_env import CrystalNN
# from ase.data import chemical_symbols, atomic_numbers
# from scipy.interpolate import CubicSpline
# from scipy.integrate import cumtrapz
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict
from matplotlib.patches import Polygon
from matplotlib import cm
from matplotlib.colors import Normalize
from mpl_toolkits.axes_grid1 import make_axes_locatable
from typing import Tuple, Union, List, Dict
import itertools

# import utils


def _get_triangle(
    coords: Tuple[int, int],
    color: Union[str, List[float]],
    is_film: bool,
):
    if is_film:
        xy = np.array(
            [
                [coords[0], coords[1]],
                [coords[0], coords[1] + 1],
                [coords[0] + 1, coords[1] + 1],
                [coords[0], coords[1]],
            ]
        )
    else:
        xy = np.array(
            [
                [coords[0], coords[1]],
                [coords[0] + 1, coords[1]],
                [coords[0] + 1, coords[1] + 1],
                [coords[0], coords[1]],
            ]
        )

    poly = Polygon(
        xy=xy,
        closed=True,
        fc=color,
        ec=(1, 1, 1, 0),
    )

    return poly


def _get_square(
    coords: Tuple[int, int],
    color: Union[str, List[float]],
):
    xy = np.array(
        [
            [coords[0], coords[1]],
            [coords[0], coords[1] + 1],
            [coords[0] + 1, coords[1] + 1],
            [coords[0] + 1, coords[1]],
            [coords[0], coords[1]],
        ]
    )

    poly = Polygon(
        xy=xy,
        closed=True,
        fc=color,
        ec=(1, 1, 1, 0),
    )

    return poly


def plot_surface_charge_matrix(
    films: SurfaceGenerator,
    substrates: SurfaceGenerator,
    output: str = "surface_charge_matrix.png",
    dpi: int = 400,
):
    film_surface_charges = [film.bottom_surface_charge for film in films]
    substrate_surface_charges = [
        substrate.bottom_surface_charge for substrate in substrates
    ]

    x_size = 4
    y_size = 4

    ratio = len(film_surface_charges) / len(substrate_surface_charges)

    if ratio < 1:
        fig_x_size = x_size
        fig_y_size = y_size / ratio
    else:
        fig_x_size = x_size * ratio
        fig_y_size = y_size

    fig, ax = plt.subplots(
        figsize=(fig_x_size, fig_y_size),
        dpi=dpi,
    )

    fontsize = 14

    ax.tick_params(labelsize=fontsize)
    ax.set_xlabel("Film Termination Index", fontsize=fontsize)
    ax.set_ylabel("Substrate Termination Index", fontsize=fontsize)

    cmap_max = np.abs(
        np.concatenate([film_surface_charges, substrate_surface_charges])
    ).max()

    cmap = cm.get_cmap("bwr")
    norm = Normalize(vmin=-cmap_max, vmax=cmap_max)

    color_mapper = cm.ScalarMappable(norm=norm, cmap=cmap)

    inds = itertools.product(range(len(films)), range(len(substrates)))

    bad_inds = []

    for ind in inds:
        film_ind = ind[0]
        sub_ind = ind[1]

        film_charge = film_surface_charges[film_ind]
        sub_charge = substrate_surface_charges[sub_ind]

        film_color = color_mapper.to_rgba(film_charge)
        sub_color = color_mapper.to_rgba(sub_charge)

        film_tri = _get_triangle(
            coords=ind,
            color=film_color,
            is_film=True,
        )
        sub_tri = _get_triangle(
            coords=ind,
            color=sub_color,
            is_film=False,
        )

        ax.add_patch(film_tri)
        ax.add_patch(sub_tri)

        if -1.0 < film_charge < 1.0:
            film_sign = 0.0
        elif film_charge <= -1.0:
            film_sign = -1.0
        elif film_charge >= 1.0:
            film_sign = 1.0

        if -1.0 < sub_charge < 1.0:
            sub_sign = 0.0
        elif sub_charge <= -1.0:
            sub_sign = -1.0
        elif sub_charge >= 1.0:
            sub_sign = 1.0

        sign_prod = sub_sign * film_sign

        if sub_sign + film_sign != 0 and sign_prod != 0:
            bad_inds.append(ind)
        #     rect = _get_square(coords=ind, color=(0, 0, 0, 0.6))
        #     ax.add_patch(rect)

    for i in range(len(film_surface_charges)):
        ax.axvline(i, color="black")

    for i in range(len(substrate_surface_charges)):
        ax.axhline(i, color="black")

    ax.set_xlim(0, len(film_surface_charges))
    ax.set_ylim(0, len(substrate_surface_charges))

    ax.set_xticks(
        ticks=np.arange(len(film_surface_charges)) + 0.5,
        labels=[str(i) for i in range(len(film_surface_charges))],
    )

    ax.set_yticks(
        ticks=np.arange(len(substrate_surface_charges)) + 0.5,
        labels=[str(i) for i in range(len(substrate_surface_charges))],
    )

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.1)
    cbar = fig.colorbar(
        color_mapper,
        cax=cax,
        orientation="vertical",
    )
    cbar.ax.tick_params(labelsize=fontsize)
    cbar.ax.locator_params(nbins=5)

    cbar.set_label(
        "Residual Surface Charge (Film/Substrate)",
        fontsize=fontsize,
        labelpad=8,
    )

    # r = 0.5  # units
    # # radius in display coordinates:
    # r_ = (
    #     ax.transData.transform([r, 0])[0] - ax.transData.transform([0, 0])[0]
    # )  # points
    # # marker size as the area of a circle
    # marker_size = 2 * r_**2

    # for film_ind, sub_ind in bad_inds:
    #     ax.scatter(
    #         [film_ind + 0.5],
    #         [sub_ind + 0.5],
    #         marker="o",
    #         fc="white",
    #         ec="black",
    #         s=2 * r_,
    #     )
    # print(marker_size)

    ax.tick_params(labelsize=fontsize)

    ax.set_aspect("equal")
    fig.tight_layout(pad=0.4)
    fig.savefig(output)
