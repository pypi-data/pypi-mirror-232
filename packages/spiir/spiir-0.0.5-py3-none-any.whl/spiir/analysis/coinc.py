"""Module for common analysis and plots used for SPIIR pipeline zerolags/triggers.

Note that all functions in this module are under development and are subject to change.
"""

import logging
from os import PathLike
from typing import Tuple, Union

import ligo.lw.ligolw
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from ..io.ligolw.array import build_psd_series_from_xmldoc, build_snr_series_from_xmldoc

logger = logging.getLogger(__name__)


def plot_snr_series(
    data: Union[str, bytes, PathLike, ligo.lw.ligolw.Document],
    title: str = "SNR series",
    figsize: Tuple[float, float] = (16, 8),
) -> Figure:
    """Plots the SNR figure from coinc file data."""
    snrs = build_snr_series_from_xmldoc(data)

    snrs = pd.concat(snrs, axis=1)

    fig, ax = plt.subplots(figsize=figsize)
    network_snr = snrs.apply(
        lambda snr: np.sqrt(np.real(snr) ** 2 + np.imag(snr) ** 2), axis=0
    )
    network_snr.plot(title=title, xlabel="Time", ylabel="SNR", ax=ax)
    ax.grid(which="both", axis="both", alpha=0.5)

    return fig


def plot_psd_series(
    data: Union[str, bytes, PathLike, ligo.lw.ligolw.Document],
    title: str = "Power Spectral Densities",
    figsize: Tuple[float, float] = (16, 8),
) -> Figure:
    """Plots the SNR figure from coinc file data."""
    psds = build_psd_series_from_xmldoc(data)

    psds = pd.concat(psds, axis=1)

    fig, ax = plt.subplots(figsize=figsize)
    psds.plot(title=title, ax=ax, logx=True, logy=True)
    ax.set(xlim=(10, psds.index.max()), xlabel="Frequency", ylabel="Amplitude")
    ax.grid(which="both", axis="both", alpha=0.5)

    return fig
