"""An abstract class to consume data from the IGWN Alert Kafka service."""
import json
import logging
from os import PathLike
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import toml
from igwn_alert import client
from ligo.gracedb.rest import GraceDb

logger = logging.getLogger(__name__)


class IGWNAlertConsumer:
    def __init__(
        self,
        topics: List[str] = ["test_spiir"],
        group: str = "gracedb-playground",
        server: str = "kafka://kafka.scima.org/",
        id: Optional[str] = None,
        username: Optional[str] = None,
        credentials: Optional[str] = None,
        upload_gracedb: bool = False,
        save_dir: Optional[Union[str, PathLike]] = None,
        save_payload: bool = False,
        upload_attempt_limit: int = 10,
    ):
        self.id = id or type(self).__name__
        self.topics = topics
        self.group = group
        self.server = server
        self.credentials = credentials or "~/.config/hop/auth.toml"
        self.username = username
        self.client = self._setup_igwn_alert_client(self.username, self.credentials)
        self.gracedb = self._setup_gracedb_client(group)
        self.upload_gracedb = upload_gracedb
        self.save_dir = Path(save_dir)  # location to save results from process_alert
        self.save_payload = save_payload
        self.upload_attempt_limit = upload_attempt_limit

    def __enter__(self):
        """Enables use within a with context block."""
        return self

    def __exit__(self, *args, **kwargs):
        """Enables use within a with context block."""
        self.close()

    def close(self):
        """Closes all client connections."""
        if self.gracedb is not None:
            self.gracedb.close()
        if self.client is not None:
            self.client.disconnect()

    def _setup_gracedb_client(self, group: Optional[str] = None):
        """Instantiate connection to GraceDb via GraceDb client."""
        groups = {"gracedb", "gracedb-test", "gracedb-playground"}
        if group is None or group not in groups:
            raise ValueError(f"gracedb must be one of {groups}, not '{group}'.")
        service_url = f"https://{group}.ligo.org/api/"
        return GraceDb(service_url=service_url, reload_certificate=True)

    def _setup_igwn_alert_client(self, username: str, credentials: str) -> client:
        """Instantiate IGWNAlert client connection."""
        # specify default SCiMMA auth.toml credentials path
        auth_fp = Path(credentials).expanduser()
        assert Path(auth_fp).is_file(), f"{auth_fp} is not a file."

        # prepare igwn alert client
        kwargs = {"server": self.server, "group": self.group, "authfile": str(auth_fp)}

        # load SCIMMA hop auth credentials from auth.toml file
        if username is not None:
            auth_data = toml.load(auth_fp)
            auth = [data for data in auth_data["auth"] if data["username"] == username]

            # handle ambiguous/duplicate usernames
            if len(auth) > 1:
                msg = f"[{self.id}] Ambiguous credentials for {username} in {auth_fp}"
                raise RuntimeError(msg)
            elif len(auth) == 0:
                msg = f"[{self.id}] No credentials found for {username} in {auth_fp}"
                raise RuntimeError(msg)
            else:
                logger.debug(
                    f"[{self.id}] Loading {username} credentials from {auth_fp}"
                )
                kwargs["username"] = auth[0]["username"]
                kwargs["password"] = auth[0]["password"]
        else:
            logger.debug(f"[{self.id}] Loading default credentials from {auth_fp}")

        return client(**kwargs)

    def _write_json(self, data: Dict[str, Any], path: Path):
        """Write dictionary data to a JSON file."""
        path.parent.mkdir(exist_ok=True, parents=True)
        with path.open(mode="w") as f:
            f.write(json.dumps(data, indent=4))

    def process_alert(
        self,
        topic: Optional[List[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
        event_id: Optional[str] = None,
    ):
        """
        Parse and process the event payload and ID.

        Parameters
        ----------
        topic : str, optional
            GraceDB topic
        payload : dict[str, Any], optional
            The payload dictionary retrieved from IGWN Alert topics.
        event_id: str, optional
            An optionally hard-coded event_id to save data for debugging.
            Set this value to None in production.
        """

        # parse payload input from topic
        if payload is None:
            logger.debug(f"[{self.id}] Alert received from {topic} without a payload.")
            return
        elif not isinstance(payload, dict):
            try:
                payload = json.loads(payload)
            except Exception as exc:
                logger.debug(f"[{self.id}] Error loading {topic} JSON payload: {exc}.")
                return

        logger.debug(f"[{self.id}] Received payload from {topic}.")

        if event_id is None:
            # here we retrieve data from IGWN alert normally if event_id is None
            # else we would proceed as normal (if event_id is provided it is for debug)

            # get GraceDb id in database to label payload and p_astro files
            try:
                event_id = payload["uid"]
            except KeyError as exc:
                logger.debug(f"[{self.id}] No uid in {topic} payload: {payload}: {exc}")
                return

        self.process_payload(payload, event_id)

    def process_payload(self, payload: Dict[str, Any], event_id: str):
        raise NotImplementedError("process_payload is an abstract function.")

    def subscribe(self, topics: Optional[List[str]] = None):
        topics = topics or self.topics
        logger.debug(f"[{self.id}] Listening to topics: {', '.join(topics)}.")
        try:
            self.client.listen(self.process_alert, topics)

        except (KeyboardInterrupt, SystemExit):
            # Kill the client upon exiting the loop:
            logger.info(f"[{self.id}] Disconnecting from: {self.server}")
            try:
                self.close()
            except Exception:
                logger.info(f"[{self.id}] Disconnected")
