"""Module for the IGWNAlert Consumer that records data from IGWN Alert and GraceDB."""

import logging
from pathlib import Path
from typing import Any, Dict

from ..consumer import IGWNAlertConsumer

logger = logging.getLogger(__name__)


class EventConsumer(IGWNAlertConsumer):
    def process_payload(self, payload: Dict[str, Any], event_id: str):
        if self.save_dir:
            Path(self.save_dir / event_id).mkdir(exist_ok=True, parents=True)

            if self.save_payload:
                payload_fp = self.save_dir / event_id / "payload.json"
                self._write_json(payload, payload_fp)
                logger.info(
                    f"[{self.id}] Saving {event_id} payload file to: {payload_fp}."
                )

            # Get list of files associated with event_id
            event_files = self.gracedb.files(event_id).json()
            for filename in list(event_files):
                save_path = self.save_dir / event_id / filename
                # Skip file if versioned or already downloaded
                if ',' in filename or filename == 'coinc.xml' or save_path.exists():
                    continue
                # Save file to event_id folder in save_dir
                response = self.gracedb.files(event_id, filename)
                outfile = open(save_path, 'wb')
                outfile.write(response.read())
                outfile.close()
                logger.info(f"[{self.id}] Saved to disk: {save_path}")
