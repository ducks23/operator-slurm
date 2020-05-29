#!/usr/bin/env python3
import os
import socket
import sys
sys.path.append('lib')
sys.path.append('../lib')

import logging

from time import sleep

from pathlib import Path

from ops.charm import CharmBase

from ops.model import ActiveStatus


from ops.framework import (
    EventSource,
    EventBase,
    Object,
    ObjectEvents,
    StoredState,
)

from slurm_snap_ops import SlurmSnapOps

from mysql_requires_interface import MySQLClient

from ops.main import main


logger = logging.getLogger()


class SlurmDBDCharm(CharmBase):
    """This charm demonstrates the 'requires' side of the relationship by
    extending CharmBase with an event object that observes
    the relation-changed hook event.
    """

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)

        self._stored.set_default(db_info=dict())

        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.install, self._on_install)

        self.db_info = MySQLClient(self, "db")
        self.framework.observe(
            self.db_info.on.db_info_available,
            self._on_db_info_available
        )

        self.slurm_ops = SlurmSnapOps(self, "slurm-config")
        self.framework.observe(
            self.slurm_ops.on.configure_slurm,
            self._on_configure_slurm
        )

    def _on_install(self, event):
        self.slurm_ops.install_slurm_snap()
        self.slurm_ops.set_slurm_snap_mode('all')
        self.unit.status = ActiveStatus("running in 'all' mode")

    def _on_start(self, event):
        pass

    def _on_db_info_available(self, event):
        """Store the db_info in the StoredState for later use.
        """
        db_info = {
            'user': event.db_info.user,
            'password': event.db_info.password,
            'host': event.db_info.host,
            'port': event.db_info.port,
            'database': event.db_info.database,
        }
        self._stored.db_info = db_info
        self.slurm_ops.on.configure_slurm.emit()
        self.unit.status = ActiveStatus("db info available")

    def _on_configure_slurm(self, event):
        """Render the slurmdbd.yaml and set the snap.mode.
        """
        hostname = socket.gethostname().split(".")[0]
        self.slurm_ops.render_slurm_config(
            f"{os.getcwd()}/src/slurmdbd.yaml.tmpl",
            "/var/snap/slurm/common/etc/slurm-configurator/slurmdbd.yaml",
            context={**{"hostname": hostname}, **self._stored.db_info}
        )
        self.unit.status = ActiveStatus("rendered to snap_common")


if __name__ == "__main__":
    main(SlurmDBDCharm)
