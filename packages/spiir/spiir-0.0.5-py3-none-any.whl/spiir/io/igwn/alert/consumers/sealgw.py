"""Module for the IGWNAlert Consumer that runs SeALGW skymap and uploads to GraceDb."""

import ctypes
import logging
import multiprocessing as mp
import time
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple

import ligo.lw
import ligo.skymap.io.fits
import numpy as np
import pandas as pd

# TODO: address the optional dependency in the __init__.py
import sealgw
import sealgw.seal

from .....io import ligolw as spiirligolw
from ..consumer import IGWNAlertConsumer

logger = logging.getLogger(__name__)

LAL_DET_MAP = dict(L1=6, H1=5, V1=2, K1=14, I1=15, CE=10, ET1=16, ET2=17, ET3=18)


class SealGWAlertConsumer(IGWNAlertConsumer):
    def __init__(
        self,
        seal_config: str,
        models: Dict[str, "sealgw.seal.Seal"],  # FIXME: Work out best way to load model
        nthreads: int = 1,
        nlevel: int = 5,  # 5->best resolution=0.013deg2; 6->0.003deg2;
        # 7->0.00008deg2 (Bayestar uses 7)
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.seal_config = seal_config
        self.models = models  # dictionary of per-source SeALGW model
        self.nthreads = mp.cpu_count() if nthreads == -1 else nthreads
        self.nlevel = nlevel

    def _get_snr_series(
        self, payload: Dict[str, Any], coinc_path: str = None
    ) -> Tuple[
        float,
        int,
        np.ndarray,
        List[str],
        float,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        np.ndarray,
        Dict[str, pd.DataFrame],
    ]:
        """
        Retrieve data for SeALGW model from the IGWNAlert payload.

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the alert.
        coinc_path : str, optional
            Path to the coinc.xml that contains the SNR series.
            If not provided, will get SNR series from the coinc.xml saved in GraceDB.

        Returns
        -------
        Tuple[float, int, np.ndarray, List[str], float, np.ndarray, np.ndarray,
            np.ndarray, np.ndarray, Dict[str, pd.DataFrame]]
            A tuple of trigger time, number of detectors, SNR array lengths,
                detector names, maximum SNRs, sigmas, time array, SNR array.

        """
        t1 = time.perf_counter()
        if coinc_path is None:
            logger.debug("Local coinc.xml not provided. Downloading from GraceDB.")
            response = self.gracedb.files(payload["uid"], 'coinc.xml')
            xmlfile_in_bytes = response.read()

            t2 = time.perf_counter()
            logger.info(f"Downloaded coinc.xml from GraceDB in {(t2-t1):.4f}s.")

            f = BytesIO(xmlfile_in_bytes)
            xmldoc = ligo.lw.utils.load_fileobj(
                f, contenthandler=spiirligolw.ligolw.LIGOLWContentHandler
            )
            xmldoc = spiirligolw.postcoh.rename_legacy_postcoh_columns(xmldoc)
            xmldoc = spiirligolw.postcoh.include_missing_postcoh_columns(
                xmldoc, nullable=True
            )
            xmldoc = spiirligolw.strip_ilwdchar(xmldoc)

            xml_tables = spiirligolw.get_tables_from_xmldoc(xmldoc)
            xml_snrs = spiirligolw.build_snr_series_from_xmldoc(xmldoc)
        else:  # use local xml if available
            xmlfile = spiirligolw.load_coinc_xml(coinc_path)
            xml_tables = xmlfile["tables"]
            xml_snrs = xmlfile["snrs"]
            t2 = time.perf_counter()
            logger.debug(f"Local coinc.xml provided. Loading cost {(t2-t1):.4f}s.")

        # FIXME: Is this the correct way of exctracting ifo names?
        #   Will it include non-triggered ifo?
        det_names = list(xml_tables['sngl_inspiral']['ifo'])

        # DO run a test (testsealgw.py) if you want to change the way of loading data
        ndet = len(det_names)
        deff_array = np.array([])
        max_snr_array = np.array([])
        det_code_array = np.array([])
        ntimes_array = np.array([])
        snr_array = np.array([])
        time_array = np.array([])

        for index, row in xml_tables['sngl_inspiral'].iterrows():
            deff_array = np.append(deff_array, row["eff_distance"])
            max_snr_array = np.append(max_snr_array, row["snr"])
            snr_array = np.append(snr_array, xml_snrs[row['ifo']])
            time_array = np.append(time_array, xml_snrs[row['ifo']].index.values)
            ntimes_array = np.append(ntimes_array, len(xml_snrs[row['ifo']]))
            det_code_array = np.append(det_code_array, int(LAL_DET_MAP[row['ifo']]))

        sigma_array = deff_array * max_snr_array

        trigger_time = list(xml_tables['coinc_inspiral']['end_time'])[0]
        trigger_time += list(xml_tables['coinc_inspiral']['end_time_ns'])[0] * 1e-9

        logger.info(f"xml processing done. Timecost {(time.perf_counter()-t2):.4f}s.")
        logger.debug(f"Trigger time: {trigger_time}")
        logger.debug(f"Detectors: {det_names}")
        logger.debug(f"SNRs: {max_snr_array}")
        logger.debug(f"sigmas: {sigma_array}")

        return (
            trigger_time,
            ndet,
            ntimes_array.astype(ctypes.c_int32),
            det_names,
            max_snr_array,
            sigma_array,
            time_array,
            snr_array,
            xml_tables,
        )

    def _localize_skymap(
        self, payload: Dict[str, Any], coinc_path: str = None, fudge_factor: float = -1
    ) -> np.ndarray:
        """Localize a GW source.

        Parameters
        ----------
        payload : dict[str, Any]
            The payload of the alert.
        coinc_path : str, optional
            Path to the coinc.xml that contains the SNR series.
            If not provided, will get SNR series from the coinc.xml saved in GraceDB.
        fudge_factor : float, default = -1
            Fudge factor by regarding [fudge_factor] condidence area as the 90% area,
            therefore shoule be a float between 0-1. -1 means no fudge factor applied.

        Returns
        -------
        np.ndarray
            The probability skymap.

        """
        try:
            data = payload["data"]["extra_attributes"]
        except Exception as exc:
            logger.debug(f"[{self.id}] No valid data retrieved from payload: {exc}.")
            return

        try:
            (
                end_time_maxsnrdet,
                ndet,
                snr_lengths,
                ifos,
                snglsnrs,
                sigmas,
                snr_times,
                snr_series,
                xml_tables,
            ) = self._get_snr_series(payload, coinc_path)
        except Exception as exc:
            logger.debug(f"[{self.id}] Error loading SNR series from payload: {exc}.")
            return

        net_snr = sum((snglsnr**2 for snglsnr in snglsnrs)) ** 0.5

        # estimate time prior
        time_prior_width = 0.01
        end_time_lower_bound = end_time_maxsnrdet - time_prior_width
        end_time_upper_bound = end_time_maxsnrdet + time_prior_width

        # check if this is consistent with bank templates
        # assumes mass_c equal across ifos and mass1 > mass2
        # Qian: yes, see https://emfollow.docs.ligo.org/userguide/content.html
        # There are multiple SingleInspiral in data, take [0]
        m1 = data["SingleInspiral"][0]["mass1"]
        m2 = data["SingleInspiral"][0]["mass2"]
        if m2 > 3:
            trigger_type = "BBH"
        elif m1 < 3:
            trigger_type = "BNS"
            # check if EW trigger
            if (
                xml_tables['process_params']
                .apply(lambda row: row.astype(str).str.contains('EW/10').any(), axis=1)
                .any()
            ):
                trigger_type = "BNS_EW_10"
            if (
                xml_tables['process_params']
                .apply(lambda row: row.astype(str).str.contains('EW/30').any(), axis=1)
                .any()
            ):
                trigger_type = "BNS_EW_30"
        else:
            trigger_type = "NSBH"
        logger.debug(
            f"Identified the source as {trigger_type}, since mass1={m1} and mass2={m2}."
        )
        try:
            source_model = self.models(self.seal_config, trigger_type)
        except Exception as exc:
            logger.debug(f"[{self.id}] Error when running seal model: {exc}.")
            return

        tcalc = time.perf_counter()
        prob_skymap = source_model.localize(
            ifos,
            snr_times,
            snr_series,
            net_snr,
            sigmas,
            snr_lengths,
            end_time_lower_bound,
            end_time_upper_bound,
            self.nthreads,
            nlevel=self.nlevel,
            interp_factor=8,
            timecost=False,
        )

        if fudge_factor > 0 and fudge_factor < 1:
            # fudge factor: regarding x% condidence area as 90%,
            # x is fudge_factor. x=0.95 in O4 PSD BNS tests.
            prob_skymap = sealgw.calculation.localization.apply_fudge_factor(
                prob_skymap, fudge_factor
            )
            logger.debug(f"Applied fudge factor {fudge_factor}.")

        logger.info(
            f"SealGW calculation done. Timecost {(time.perf_counter()-tcalc):.4f}s."
        )

        return prob_skymap

    def process_payload(
        self,
        payload: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
        coinc_path: Optional[str] = None,
        save_fits: Optional[bool] = True,
        save_png: Optional[bool] = True,
        fudge_factor: Optional[float] = -1,
    ):
        """
        Process IGWN Alerts by retrieving coinc.xml files and computing skymap.

        Parameters
        ----------
        payload : dict[str, Any], optional
            The payload dictionary retrieved from IGWN Alert topics.
        event_id: str, optional
            An optionally hard-coded event_id to save data for debugging.
            Set this value to None in production.
        coinc_path : str, optional
            Path to the coinc.xml that contains the SNR series.
            If not provided, will get SNR series from the coinc.xml saved in GraceDB.
        save_fits: bool, default = True
            Save .fits or not.
        save_png: bool, default = False
            Save skymap plot or not. Warning: this could be time consuming!
        fudge_factor: float, default = -1
            Fudge factor by regarding [fudge_factor] condidence area as the 90% area,
            therefore shoule be a float between 0-1. -1 means no fudge factor applied.
        """
        runtime = time.perf_counter()

        prob_skymap = self._localize_skymap(payload, coinc_path, fudge_factor)

        if prob_skymap is not None:
            if save_fits:
                # FIXME: correct the vcs_revision etc, make sure .fits has
                # required metadata
                save_fits_runtime = time.perf_counter()

                sealgw_fitsfp = f"{self.save_dir}/{event_id}_sealgw.fits"
                now = datetime.now()

                prob_skymap_den_table = (
                    sealgw.calculation.multiorder4fits.probskymap2UNIQTable(prob_skymap)
                )

                dt_string = now.strftime("%Y-%m-%dT%H:%M:%S")
                ligo.skymap.io.fits.write_sky_map(
                    sealgw_fitsfp,
                    prob_skymap_den_table,
                    nest=True,
                    vcs_version='SealGW 0.01',
                    vcs_revision='bar',
                    build_date=dt_string,
                )

                save_fits_runtime = time.perf_counter() - save_fits_runtime
                logger.debug(f"{sealgw_fitsfp} saved, cost {save_fits_runtime:.4f}s.")

                if self.upload_gracedb:
                    logger.info(
                        f"[{self.id}] Uploading {event_id} SealGW fits to {self.group}."
                    )
                    for i in range(1, self.upload_attempt_limit + 1):
                        try:
                            self.gracedb.writeLog(
                                event_id,
                                "SealGW fits",
                                filename=sealgw_fitsfp,
                                tag_name="sky_loc"
                                # label="SKYMAP_READY",
                            )
                            break
                        except Exception as e:
                            logger.error(
                                "[%d/%d] gracedb SealGW fits upload failed"
                                % (i, self.upload_attempt_limit)
                            )
                            logger.error(e)
                            time.sleep(1)

            if save_png:
                # FIXME: plot skymap is extremely slow... why?
                save_png_runtime = time.perf_counter()

                sealgw_fp = f"{self.save_dir}/{event_id}_sealgw.png"
                sealgw.calculation.localization.plot_skymap(
                    prob_skymap, str(sealgw_fp), title=f"{event_id} SealGW skymap"
                )

                save_png_runtime = time.perf_counter() - save_png_runtime
                logger.debug(f"{sealgw_fp} saved, cost {save_png_runtime:.4f}s.")

                if self.upload_gracedb:
                    logger.info(
                        f"""[{self.id}] Uploading {event_id} SealGW skymap
                        to {self.group}."""
                    )
                    for i in range(1, self.upload_attempt_limit + 1):
                        try:
                            self.gracedb.writeLog(
                                event_id,
                                "SealGW skymap",
                                filename=sealgw_fp,
                                tag_name="sky_loc",
                            )
                            break
                        except Exception as e:
                            logger.error(
                                "[%d/%d] gracedb SealGW skymap upload failed"
                                % (i, self.upload_attempt_limit)
                            )
                            logger.error(e)
                            time.sleep(1)

            runtime = time.perf_counter() - runtime
            logger.debug(
                f"[{self.id}] Alert for {event_id} processed in {runtime:.4f}s."
            )
        else:
            logger.debug(
                f"""[{self.id}] Alert for {event_id} failed to process in
                {runtime:.4f}s. prob_skymap is None."""
            )
