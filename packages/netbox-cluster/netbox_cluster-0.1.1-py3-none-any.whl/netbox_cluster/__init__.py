from extras.plugins import PluginConfig


__author__ = "Pat McLean"
__email__ = "patrick.mclean@sap.com"
__version__ = "0.0.1"

class DeviceClusterConfig(PluginConfig):
    name = 'netbox_cluster'
    verbose_name = 'Device Clusters'
    description = 'A Netbox Plugin to allow for device cluster management, i.e. Oracle RAC, Windows, Cisco vPC'
    version = '0.1'
    author = __author__
    author_email = __email__
    version = __version__
    base_url = "clusters"
    min_version = "3.5.0"


config = DeviceClusterConfig