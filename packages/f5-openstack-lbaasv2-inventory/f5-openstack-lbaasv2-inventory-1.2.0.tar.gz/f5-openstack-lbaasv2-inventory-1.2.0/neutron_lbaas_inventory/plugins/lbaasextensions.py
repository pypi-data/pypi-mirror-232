from oslo_log import log

from neutron_lbaas_inventory.extensions import base
from neutron_lbaas_inventory.db.inventory_db import InventoryDbPlugin

from neutron_lib import constants as n_constants
from neutron_lib.plugins import directory
from neutron_lbaas.db.loadbalancer import loadbalancer_dbv2 as ldbv2
from neutron_lbaas.db.loadbalancer import models

LOG = log.getLogger(__name__)


class LbaasExtensionsPlugin(base.LbaasExtensionsPluginBase):

    supported_extension_aliases = [
        "lbaas-extensions", "lbaas-device"
    ]
    inventory_db = InventoryDbPlugin()

    def __init__(self):
        self.db = ldbv2.LoadBalancerPluginDbv2()

    def _get_lbass_plugin(self):
        service_plugins = directory.get_plugins()
        return service_plugins.get('LOADBALANCERV2')

    def _get_lbaas_drivers(self):
        lbaas_plugin = self._get_lbass_plugin()
        return lbaas_plugin.drivers

    # we only have one driver provider in NG
    def _get_lbaas_driver(self, name='f5networks'):
        drivers = self._get_lbaas_drivers()
        return drivers[name]

    def rebuild(self, context, lb_id, body):

        self.db.test_and_set_status(context, models.LoadBalancer, lb_id,
                                    n_constants.PENDING_UPDATE)

        lb_db = self.db.get_loadbalancer(context, lb_id)

        provider_name = lb_db.provider.provider_name
        LOG.debug("Get provider %s for %s" %
                  (provider_name, lb_id))
        f5driver = self._get_lbaas_driver(provider_name)

        body['loadbalancerext']['loadbalancer'] = lb_db
        rebuild_method = f5driver.load_balancer.refresh

        self._call_driver_operation(context, rebuild_method, body)

        return lb_db.to_api_dict()

    def get_loadbalancer(self, context, id, fields=None):
        return self.db.get_loadbalancer(context, id).to_api_dict()

    def _call_driver_operation(self, context, driver_method, db_entity,
                               old_db_entity=None, **kwargs):
        lbaas_plugin = self._get_lbass_plugin()
        lbaas_plugin._call_driver_operation(
            context, driver_method, db_entity, old_db_entity, **kwargs)

    # lbaas devices related
    def get_devices(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
        LOG.debug("List lbaas devices")
        devices = self.inventory_db.get_devices(context, filters=filters)
        return devices

    def get_device(self, context, id, fields=None):
        LOG.debug("Get a lbaas device, id: {}".format(id))
        return self.inventory_db.get_device(context, id)

    def create_device(self, context, device):
        LOG.debug("Create lbaas device, device_info: {}".format(device))
        return self.inventory_db.create_device(context, device)

    def delete_device(self, context, id):
        LOG.debug("Delete lbaas device, id: {}".format(id))
        self.inventory_db.delete_device(context, id)

    def update_device(self, context, id, device):
        LOG.debug("Update lbaas device, id: {}, device: {}".format(id, device))
        return self.inventory_db.update_device(context, id, device)

    def get_loadbalanceragentbindings(self, context, filters=None, fields=None,
                                      sorts=None, limit=None, marker=None,
                                      page_reverse=False):
        LOG.debug("List loadbalancer device bindings")
        lb_device_bindings = self.inventory_db.get_bindings(context,
                                                            filters=filters)
        return lb_device_bindings

    def get_device_members(self, context, device_id, filters=None,
                           fields=None):
        LOG.debug("Get lbaas device members, device_id: {}".format(device_id))
        filters['device_id'] = [device_id]
        return self.inventory_db.get_members(context, filters=filters)

    def get_device_member(self, context, id, device_id, fields=None):
        LOG.debug("Get lbaas device member, device_id: {}, id: {}"
                  .format(device_id, id))
        return self.inventory_db.get_member(context, id)

    def create_device_member(self, context, device_id, member):
        LOG.debug("Create lbaas device member, device_id: {}, member: {}"
                  .format(device_id, member))
        return self.inventory_db.create_member(context, device_id, member)

    def update_device_member(self, context, id, device_id, member):
        LOG.debug("Update lbaas device member, device_id: {}, id: {}"
                  .format(device_id, id))
        return self.inventory_db.update_member(context, id, member)

    def delete_device_member(self, context, id, device_id=None):
        LOG.debug("Delete lbaas device member, device_id: {}, id: {}"
                  .format(device_id, id))
        self.inventory_db.delete_member(context, id)
