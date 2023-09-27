"""Module for the IGWNAlert Consumer that predicts p_astro and uploads to GraceDb."""

import logging
import time
from typing import TYPE_CHECKING, Any, Dict

from ..consumer import IGWNAlertConsumer

if TYPE_CHECKING:
    from ....search.p_astro.models import CompositeModel

logger = logging.getLogger(__name__)


class PAstroAlertConsumer(IGWNAlertConsumer):
    def __init__(self, model: "CompositeModel", **kwargs):
        super().__init__(**kwargs)
        self.model = model  # assumes p-astro model already loaded

    def _get_data_from_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve data for p_astro model from the IGWNAlert payload."""
        try:
            data = payload["data"]["extra_attributes"]
        except Exception as exc:
            logger.debug(f"[{self.id}] No valid data retrieved from payload: {exc}.")
            return

        far = data["CoincInspiral"]["combined_far"]
        if far <= 0.0:
            logger.debug(f"[{self.id}] FAR is equal to 0. - skipping")
            return

        snr = data["CoincInspiral"]["snr"]
        mchirp = data["CoincInspiral"]["mchirp"]
        eff_dist = min(sngl["eff_distance"] for sngl in data["SingleInspiral"])

        return {"far": far, "snr": snr, "mchirp": mchirp, "eff_dist": eff_dist}

    def process_payload(self, payload: Dict[str, Any], event_id: str):
        """Process IGWN Alerts by retrieving coinc.xml files and computing p_astro."""
        runtime = time.perf_counter()

        data = self._get_data_from_payload(payload)
        if data is None:
            return

        # compute p_astro
        p_astro = self.model.predict(**data)

        # create spiir.p_astro.json file and upload to GraceDb
        p_astro_fp = self.save_dir / event_id / "spiir.p_astro.json"
        self._write_json(p_astro, p_astro_fp)

        if self.upload_gracedb:
            logger.info(f"[{self.id}] Uploading {event_id} p_astro to {self.group}.")
            for i in range(1, self.upload_attempt_limit + 1):
                try:
                    self.gracedb.writeLog(
                        event_id,
                        "source probabilities",
                        filename=p_astro_fp,
                        label="PASTRO_READY",
                        tag_name="p_astro",
                    )
                    break
                except Exception as e:
                    logger.error(
                        "[%d/%d] gracedb p_astro upload failed"
                        % (i, self.upload_attempt_limit)
                    )
                    logger.error(e)
                    time.sleep(1)

        runtime = time.perf_counter() - runtime
        logger.debug(f"[{self.id}] Alert for {event_id} processed in {runtime:.4f}s.")
