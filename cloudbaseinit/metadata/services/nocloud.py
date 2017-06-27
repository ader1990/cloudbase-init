# Copyright 2012 Cloudbase Solutions Srl
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import yaml

from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.metadata.services import driveservice
from cloudbaseinit.metadata.services import ec2service
from cloudbaseinit.metadata.services.osconfigdrive import base as basecd

LOG = oslo_logging.getLogger(__name__)
CONF = cloudbaseinit_conf.CONF


class NoCloudConfigDriveService(driveservice.DriveService,
                                ec2service.EC2Service):

    def __init__(self):
        super(NoCloudConfigDriveService, self).__init__(
            config_type=basecd.NOCLOUD_CONFIG_DRIVE)

    def get_user_data(self):
        return self._get_cache_data("user-data")

    def _get_meta_data(self):
        data = self._get_cache_data("meta-data", decode=True)
        if data:
            return yaml.load(data)
        return dict()

    def _get_config_options(self):
        self._searched_types = set(CONF.nocloud.types)
        self._searched_locations = set(CONF.nocloud.locations)

        # Deprecation backward compatibility.
        if CONF.nocloud.raw_hdd:
            self._searched_types.add("iso")
            self._searched_locations.add("hdd")
        if CONF.nocloud.cdrom:
            self._searched_types.add("iso")
            self._searched_locations.add("cdrom")
        if CONF.nocloud.vfat:
            self._searched_types.add("vfat")
            self._searched_locations.add("hdd")

    def get_host_name(self):
        return self._get_meta_data().get('local-hostname')

    def get_instance_id(self):
        return self._get_meta_data().get('instance-id')

    def get_public_keys(self):
        return self._get_meta_data().get('public-keys')
