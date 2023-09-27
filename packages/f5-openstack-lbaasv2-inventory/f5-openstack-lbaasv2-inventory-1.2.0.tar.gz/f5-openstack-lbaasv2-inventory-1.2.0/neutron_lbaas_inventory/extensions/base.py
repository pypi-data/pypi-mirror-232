# -*- coding: utf-8 -*-

import abc
import six

from neutron_lib.services import base as service_base
from neutron_lbaas_inventory.common import constants


@six.add_metaclass(abc.ABCMeta)
class LbaasExtensionsPluginBase(service_base.ServicePluginBase):
    # use /v2.0/lbaas-exts/loadbalancers
    path_prefix = constants.LBAAS_EXTS_PREFIX

    def get_plugin_name(self):
        return constants.LBAAS_EXTS

    def get_plugin_type(self):
        return constants.LBAAS_EXTS

    def get_plugin_description(self):
        return "support for lbaas customized extension " \
            "management"

    # extend 'rebuild' action
    @abc.abstractmethod
    def rebuild(self, context, id, body):
        pass

    @abc.abstractmethod
    def get_devices(self, context, filters=None, fields=None,
                    sorts=None, limit=None, marker=None,
                    page_reverse=False):
        pass

    @abc.abstractmethod
    def get_device(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def create_device(self, context, device):
        pass

    @abc.abstractmethod
    def delete_device(self, context, id):
        pass

    @abc.abstractmethod
    def update_device(self, context, id, device):
        pass

    @abc.abstractmethod
    def get_loadbalanceragentbindings(self, context, filters=None, fields=None,
                                      sorts=None, limit=None, marker=None,
                                      page_reverse=False):
        pass

    @abc.abstractmethod
    def get_device_members(self, context, device_id, filters=None,
                           fields=None):
        pass

    @abc.abstractmethod
    def get_device_member(self, context, id, device_id, fields=None):
        pass

    @abc.abstractmethod
    def create_device_member(self, context, device_id, member):
        pass

    @abc.abstractmethod
    def update_device_member(self, context, id, device_id, member):
        pass

    @abc.abstractmethod
    def delete_device_member(self, context, id, device_id=None):
        pass
