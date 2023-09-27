from neutron.api import extensions as neutron_extensions
from neutron.api.v2 import resource_helper
from neutron_lib.api import extensions as api_extensions
from oslo_log import log as logging

from neutron_lbaas_inventory.extensions import base
from neutron_lbaas_inventory import extensions as device_extensions
from neutron_lbaas_inventory.common import constants

# Ensure the extension is loaded at startup
neutron_extensions.append_api_extensions_path(device_extensions.__path__)

LOG = logging.getLogger(__name__)

RESOURCE_ATTRIBUTE_MAP = {
    'loadbalancers': {
        'id': {'allow_post': False, 'allow_put': False,
               'validate': {'type:uuid': None},
               'is_visible': True,
               'primary_key': True}
    }
}


class Lbaasextensions(api_extensions.ExtensionDescriptor):
    """API extension for handling lbaas device."""

    @classmethod
    def get_name(cls):
        return "Lbaas Extensions"

    @classmethod
    def get_alias(cls):
        return "lbaas-extensions"

    @classmethod
    def get_description(cls):
        return "Provides a REST API for lbaas customized " \
               "extensions operators to manage devices."

    @classmethod
    def get_updated(cls):
        return "2023-07-18T00:00:00-00:00"

    @classmethod
    def get_resources(cls):
        plural_mappings = resource_helper.build_plural_mappings(
            {}, RESOURCE_ATTRIBUTE_MAP)
        action_map = {'loadbalancer': {'rebuild': "POST"}}
        # bind service plugin name
        which_plugin = constants.LBAAS_EXTS

        resources = resource_helper.build_resource_info(
            plural_mappings,
            RESOURCE_ATTRIBUTE_MAP,
            which_plugin,
            action_map=action_map,
            register_quota=False)
        return resources

    @classmethod
    def get_plugin_interface(cls):
        return base.LbaasExtensionsPluginBase

    def get_extended_resources(self, version):
        if version == "2.0":
            return RESOURCE_ATTRIBUTE_MAP
        else:
            return {}
