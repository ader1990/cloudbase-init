# Copyright 2017 Cloudbase Solutions Srl
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

from cloudbaseinit.osutils import factory
from cloudbaseinit.plugins.common.userdataplugins.cloudconfigplugins import (
    base
)
from cloudbaseinit.utils import hostname


LOG = oslo_logging.getLogger(__name__)

PHONE_HOME_POST_LIST_ALL = [
    'instance_id',
    'hostname',
    'fqdn',
]

class PhoneHomePlugin(base.BaseCloudConfigPlugin):
    """Call a specific URL with a specific POST payload.

    Phone home is a feature that allows the underlying cloud to know
    when a specific instance has reached the ready state.

    If the phone_home url contains the string ``$INSTANCE_ID`` it will be replaced with
    the id of the current instance. Either all data can be posted or a list of keys to post.
    Available keys are:
        - instance_id
        - hostname
        - fqdn
    """

    def process(self, data, service):
        osutils = factory.get_os_utils()
        phone_home_post_data_entries = []
        phone_home_post_body = {}

        phone_home_url = data.get('url')
        phone_home_post_body = data.get('post')
        phone_home_retries = data.get('tries')

        phone_home_available_data = {}
        phone_home_available_data['instance_id'] = service.get_instance_id()
        phone_home_available_data['hostname'] = osutils.get_hostname()
        phone_home_available_data['fqdn'] = osutils.get_hostname(fqdn=True)
        if not phone_home_url:
            LOG.debug("Phone home url not present. Insufficient data to phone home.")
            return
        phone_home_url = phone_home_url.replace('$INSTANCE_ID', phone_home_available_data.get('instance_id'))

        if not phone_home_retries:
            phone_home_retries = CONF.default.phone_home_retries
        
        if phone_home_post and phone_home_post == 'all':
                phone_home_post_data_entries = PHONE_HOME_POST_LIST_ALL
        if phone_home_post_data_entries:
            for key in phone_home_post_data_entries:
                phone_home_post_body[key] = phone_home_available_data[key]
 
        LOG.info("Calling home to url %s with data %r", phone_home_url, phone_home_post_body)
        try:
            action = lambda: service._http_request(
                phone_home_url, json.dumps(phone_home_post_body))
            return service._exec_with_retry(action)
        except error.HTTPError:
            LOG.error("Failed to call home to the metadata service")
            raise
        else:
            raise
