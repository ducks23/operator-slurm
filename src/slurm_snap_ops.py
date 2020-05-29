from ops.framework import (
    EventSource,
    EventBase,
    Object,
    ObjectEvents,
)

from pathlib import Path

import subprocess

import os

class ConfigureSlurmEvent(EventBase):
    """Event used to signal that slurm config should be written to disk.
    """

class SlurmSnapInstalledEvent(EventBase):
    """Event used to signal that the slurm snap has been installed.
    """

class ConfigureSlurmEvents(ObjectEvents):
    configure_slurm = EventSource(ConfigureSlurmEvent)
    slurm_snap_installed = EventSource(SlurmSnapInstalledEvent)


class SlurmSnapOps(Object):
    """Class containing events used to signal slurm snap configuration.

    Events emitted:
        - configure_slurm
    """
    on = ConfigureSlurmEvents()

    def install_slurm_snap(self):
        #cmd = ["snap", "install"]
        #resource = resource_get("slurm")

        #if resource is not False:
        #    cmd.append(resource)
        #    cmd.append("--dangerous")
        #    cmd.append("--classic")
        #else:
        #    cmd.append("slurm")

        #subprocess.call(cmd)
        #change this dude
        subprocess.call(["snap", "install", "slurm"])
        subprocess.call(["snap", "connect", "slurm:network-control"])
        subprocess.call(["snap", "connect", "slurm:system-observe"])
        subprocess.call(["snap", "connect", "slurm:hardware-observe"])

    def render_slurm_config(self, source, target, context):
        """Render the context into the source template and write
        it to the target location.
        """

        source = Path(source)
        target = Path(target)

        if context and type(context) == dict:
            ctxt = context
        else:
            raise TypeError(
                f"Incorect type {type(context)} for context - Please debug."
            )

        if not source.exists():
            raise Exception(
                f"Source config {source} does not exist - Please debug."
            )

        if target.exists():
            target.unlink()

        with open(str(target), 'w') as f:
            f.write(open(str(source), 'r').read().format(**ctxt))


    def set_slurm_snap_mode(self, snap_mode):
        subprocess.call(["snap", "set", "slurm", snap_mode])

        pass

def resource_get(resource_name):
    '''Used to fetch the resource path of the given name.
    This wrapper obtains a resource path and adds an additional
    check to return False if the resource is zero length.
    '''
    res_path = subprocess.run(
        [
            'resource-get',
            resource_name
        ]
    )
    if res_path and os.stat(res_path).st_size != 0:
        return res_path
    return False

