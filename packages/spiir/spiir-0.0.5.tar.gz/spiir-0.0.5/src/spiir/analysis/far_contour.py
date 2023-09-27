import logging
from os import PathLike
from typing import Optional, Sequence, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

from spiir.io.ligolw.array import get_arrays_from_xmldoc
from spiir.io.ligolw.ligolw import load_ligolw_xmldoc
from spiir.io.ligolw.param import get_params_from_xmldoc
from spiir.io.ligolw.table import get_exact_table_from_xmldoc, load_table_from_xmls

logger = logging.getLogger(__name__)


def get_step(max: float, min: float, num_bins: int):
    return (max - min) / (num_bins - 1)


def convert_rankmap_to_fapmap(
    rankmap: np.ndarray, rankfap: np.ndarray, rankrate_table: pd.DataFrame
) -> np.ndarray:
    # LOGRANK_CMIN, LOGRANK_CMAX, LOGRANK_NBIN may all be read from file.
    rank_step = get_step(
        rankrate_table["cmax"][0], rankrate_table["cmin"][0], rankrate_table["nbin"][0]
    )
    fapmap = np.zeros(rankmap.shape)
    for ix in range(0, rankmap.shape[0]):
        for iy in range(0, rankmap.shape[1]):
            rank = rankmap[ix, iy]
            rank_idx = int(
                min(
                    max(rank - rankrate_table["cmin"][0], 0) / rank_step,
                    rankrate_table["nbin"][0] - 1,
                )
            )
            fapmap[ix, iy] = rankfap[rank_idx]
    return fapmap


def create_far_contour_plot(
    log_farmap: np.ndarray,
    event_cohsnr: float,
    event_chisq: float,
    title: str = "FAR Contours",
    all_cohsnr: Optional[np.ndarray] = None,
    all_chisq: Optional[np.ndarray] = None,
    snr_min: float = 0.54,
    snr_max: float = 3.0,
    chisq_min: float = -1.2,
    chisq_max: float = 3.5,
) -> Figure:
    fig, ax = plt.subplots(figsize=(12, 8), layout="tight")

    levels = np.arange(-13, -2, 2)
    CS = ax.contour(
        log_farmap,
        levels,
        origin='lower',
        extent=(snr_min, snr_max, chisq_min, chisq_max),
    )
    fig.colorbar(CS, shrink=0.8, extend='both')

    if all_cohsnr is not None and all_chisq is not None:
        CM = ax.scatter(
            all_cohsnr, all_chisq, color='k', marker='o', s=6, facecolors='none'
        )
        CM2 = ax.scatter(
            event_cohsnr, event_chisq, color='r', marker='*', s=100, facecolors='none'
        )
        ax.legend(
            (CM, CM2), ('all spiir zerolags', 'this spiir event'), loc='lower right'
        )
    else:
        CM2 = ax.scatter(
            event_cohsnr, event_chisq, color='r', marker='*', s=100, facecolors='none'
        )
        ax.legend((CM2,), ('this spiir event',), loc='lower right')

    ax.set(
        xlim=(0.5, 2.2),
        ylim=(-0.8, 1),
        xlabel=r'$\log_{10}(\rho_c)$',
        ylabel=r'$\log_{10}(\xi_c^2)$',
        title=title,
    )

    return fig


def plot_far_contours(
    ifos: str,
    stats_path: Union[str, bytes, PathLike],
    far_factor: float,
    snr: float,
    chisq: float,
    zerolags_paths: Optional[Sequence[Union[str, bytes, PathLike]]] = None,
    snr_min: float = 0.54,
    snr_max: float = 3.0,
    chisq_min: float = -1.2,
    chisq_max: float = 3.5,
    verbose: bool = False,
) -> Figure:
    """Plot FAR contours from a valid with a scatter plot of triggers.

    Parameters
    ----------
    ifos: str
        A string with each IFO in the order it appears in the LIGO_LW documents.
        e.g. H1L1V1K1.
    stats_path: str | bytes | PathLike
        A path-like to a file containing a valid Marginailzed Stats file.
    far_factor: float
        Normalization factor for false alarm rate threshold.
        Typically the number of compute nodes for the source.
    snr: float
        The SNR of the event.
    chisq: float
        The chisq of the event.
    zerolags_paths: [Sequence[Union[str, bytes, PathLike]]], optional
        A list of valid LIGO_LW XML zerolag files to include on the scatter plot.
        If a single IFO is provided, the sngl snr and chisq columns will be plotted.
        If multiple IFOs are provided, the cohsnr and cmbchisq columns will be used.
    snr_min: float, optional
        Min log snr for contours. Should correspond to snr bins in the stats file.
    snr_max: float, optional
        Max log snr for contours. Should correspond to snr bins in the stats file.
    chisq_min: float, optional
        Min log chisq for contours. Should correspond to chisq bins in the stats file.
    chisq_max: float, optional
        Max log chisq for contours. Should correspond to chisq bins in the stats file.

    Returns
    -------
    matplotlib.figure.Figure
        The FAR contour plot with event and optional zerolags scatter plot.
    """
    ifos_lowercase = ifos.lower()
    ifos_uppercase = ifos.upper()

    # load fields from background stats xml file
    background_rank_name = "background_rank"
    background_feature_name = "background_feature"
    rank_map_suffix = "rank_map"
    rank_fap_suffix = "rank_fap"
    rankmap_name = f"{background_rank_name}:{ifos_uppercase}_{rank_map_suffix}"
    rankfap_name = f"{background_rank_name}:{ifos_uppercase}_{rank_fap_suffix}"
    nevent_name = f"{background_feature_name}:{ifos_lowercase}_nevent"
    livetime_name = f"{background_feature_name}:{ifos_lowercase}_livetime"
    hist_trials_name = f"{background_feature_name}:hist_trials"

    xmldoc = load_ligolw_xmldoc(stats_path)
    stats_arrays = get_arrays_from_xmldoc(xmldoc, [rankmap_name, rankfap_name])
    stats_params = get_params_from_xmldoc(
        xmldoc, [nevent_name, livetime_name, hist_trials_name]
    )

    rankrate_name = f"{background_rank_name}:rank_rate:table"
    rankrate_table = get_exact_table_from_xmldoc(xmldoc, rankrate_name)

    # load the zerolag file for comparison
    all_cohsnr = None
    all_chisq = None
    if zerolags_paths is not None:
        zerolags = load_table_from_xmls(zerolags_paths, "postcoh", verbose=verbose)
        if len(ifos) == 1:  # single detector event
            snr_name = 'snglsnr_sngl_%s' % ifos_uppercase[0]
            chisq_name = 'chisq_sngl_%s' % ifos_uppercase[0]
            all_cohsnr = np.log10(zerolags[snr_name])
            all_chisq = np.log10(zerolags[chisq_name])
        else:
            all_cohsnr = np.log10(zerolags["cohsnr"])
            all_chisq = np.log10(zerolags["cmbchisq"])

    # get the event cohsnr and chisq from options
    event_cohsnr = np.log10(snr)
    event_chisq = np.log10(chisq)

    x_step = get_step(snr_max, snr_min, rankrate_table["nbin"][0])
    cohsnr_idx = int(
        min(
            max(event_cohsnr - snr_min, 0) / x_step,
            rankrate_table["nbin"][0] - 1,
        )
    )

    y_step = get_step(chisq_max, chisq_min, rankrate_table["nbin"][0])
    chisq_idx = int(
        min(
            max(event_chisq - chisq_min, 0) / y_step,
            rankrate_table["nbin"][0] - 1,
        )
    )

    # FIXME: convert rankmap to rankfap

    fapmap = convert_rankmap_to_fapmap(
        stats_arrays[rankmap_name], stats_arrays[rankfap_name], rankrate_table
    )
    farmap = (
        fapmap
        * stats_params[nevent_name]
        / (float(stats_params[livetime_name]) * stats_params[hist_trials_name])
        * float(far_factor)
    )
    lgfarmap = np.log10(farmap)

    event_far = farmap[chisq_idx, cohsnr_idx]
    logger.info(f"event far '{event_far}'")

    return create_far_contour_plot(
        lgfarmap,
        event_cohsnr,
        event_chisq,
        title=f"{ifos} Background nevent {stats_params[nevent_name]}, "
        f"livetime {stats_params[livetime_name]}",
        all_cohsnr=all_cohsnr,
        all_chisq=all_chisq,
        snr_min=snr_min,
        snr_max=snr_max,
        chisq_min=chisq_min,
        chisq_max=chisq_max,
    )
