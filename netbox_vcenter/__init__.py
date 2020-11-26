VERSION = '0.1.1'

try:
    from extras.plugins import PluginConfig
except ImportError:
    # Dummy for when importing outside of netbox
    class PluginConfig:
        pass


class NetBoxVCenterConfig(PluginConfig):
    name = 'netbox_vcenter'
    verbose_name = 'vCenter'
    version = VERSION
    author = 'Sander Steffann'
    author_email = 'sander@steffann.nl'
    description = 'vCenter integration for NetBox'
    base_url = 'vcenter'
    required_settings = []
    default_settings = {
        'CACHE_TIMEOUT': 3600,
        'CACHE_FAILURE_TIMEOUT': 600,
        'REFRESH_WAIT': 15,
    }


config = NetBoxVCenterConfig
