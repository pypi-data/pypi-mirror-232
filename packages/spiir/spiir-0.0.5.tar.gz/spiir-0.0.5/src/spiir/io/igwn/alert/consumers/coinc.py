"""Module for the IGWNAlert Consumer to process coinc data and upload to GraceDB."""

import logging
import time
from io import BytesIO
from typing import Any, Dict

import ligo.lw
import ligo.skymap.io.fits

from .....analysis import coinc
from .....io import ligolw as spiirligolw
from ..consumer import IGWNAlertConsumer

logger = logging.getLogger(__name__)


class CoincConsumer(IGWNAlertConsumer):
    def process_payload(self, payload: Dict[str, Any], event_id: str):
        # only get the first alert for a given event - initial coinc.xml upload
        if payload.get("alert_type", None) != "new":
            return

        t1 = time.perf_counter()

        logger.debug("Local coinc.xml not provided. Downloading from GraceDB.")
        response = self.gracedb.files(payload["uid"], 'coinc.xml')
        xmlfile_in_bytes = response.read()

        t2 = time.perf_counter()
        logger.info(f"Downloaded coinc.xml from GraceDB in {(t2-t1):.4f}s.")

        f = BytesIO(xmlfile_in_bytes)
        xmldoc = ligo.lw.utils.load_fileobj(
            f, contenthandler=spiirligolw.ligolw.LIGOLWContentHandler
        )
        xmldoc = spiirligolw.strip_ilwdchar(xmldoc)

        self.save_dir.mkdir(exist_ok=True, parents=True)

        snr_series_fp = f"{self.save_dir}/{event_id}_snr_series.png"
        fig = coinc.plot_snr_series(xmldoc)
        fig.savefig(snr_series_fp)
        if self.upload_gracedb:
            logger.info(f"[{self.id}] Uploading {event_id} SNR series to {self.group}.")
            for i in range(1, self.upload_attempt_limit + 1):
                try:
                    self.gracedb.writeLog(
                        event_id, "SNR series", filename=snr_series_fp, tag_name="psd"
                    )
                    break
                except Exception as e:
                    logger.error(
                        "[%d/%d] gracedb SNR series upload failed"
                        % (i, self.upload_attempt_limit)
                    )
                    logger.error(e)
                    time.sleep(1)

        psd_series_fp = f"{self.save_dir}/{event_id}_psd_series.png"
        fig = coinc.plot_psd_series(xmldoc)
        fig.savefig(psd_series_fp)
        if self.upload_gracedb:
            logger.info(f"[{self.id}] Uploading {event_id} PSD series to {self.group}.")
            for i in range(1, self.upload_attempt_limit + 1):
                try:
                    self.gracedb.writeLog(
                        event_id, "PSD series", filename=psd_series_fp, tag_name="psd"
                    )
                    break
                except Exception as e:
                    logger.error(
                        "[%d/%d] gracedb PSD series upload failed"
                        % (i, self.upload_attempt_limit)
                    )
                    logger.error(e)
                    time.sleep(1)

        runtime = time.perf_counter() - t1
        logger.debug(f"[{self.id}] Alert for {event_id} processed in {runtime:.4f}s.")
