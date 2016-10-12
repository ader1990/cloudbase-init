# Copyright 2016 Cloudbase Solutions Srl
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

from oslo_log import log as oslo_logging

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.osutils import factory as osutils_factory
from cloudbaseinit.plugins.common import base
from cloudbaseinit.plugins.common import setserviceuser

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)

class SetServiceUserPlugin(setserviceuser.SetServiceUserPlugin):

    def execute(self, service, shared_data):
        osutils = osutils_factory.get_os_utils()
        if CONF.service_username and CONF.service_name:
            LOG.debug('Generating a random user password')
            maximum_length = osutils.get_maximum_password_length()
            password = osutils.generate_random_password(
                maximum_length)

            osutils.set_user_password(CONF.service_username, password)
        
            if osutils.check_service_exists(CONF.service_name):
                LOG.debug("Setting service username and password")
                osutils.set_service(CONF.service_name,
                    ".\{}".format(CONF.service_username), password)
        return base.PLUGIN_EXECUTION_DONE, False
