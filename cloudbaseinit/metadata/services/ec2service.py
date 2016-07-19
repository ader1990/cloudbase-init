# Copyright 2014 Cloudbase Solutions Srl
# Copyright 2012 Mirantis Inc.
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

from oslo_config import cfg
from oslo_log import log as oslo_logging

from cloudbaseinit.metadata.services import base
from cloudbaseinit.utils import network

opts = [
    cfg.StrOpt('ec2_metadata_base_url',
               default='http://169.254.169.254/',
               help='The base URL where the service looks for metadata'),
    cfg.BoolOpt('ec2_add_metadata_private_ip_route', default=True,
                help='Add a route for the metadata ip address to the gateway'),
]

CONF = cfg.CONF
CONF.register_opts(opts)

LOG = oslo_logging.getLogger(__name__)

HOST_NAME = 'hostname'
INSTANCE_ID = 'instance-id'
PUBLIC_KEYS = 'public-keys'


class EC2Service(base.BaseHTTPMetadataService):

    """Metadata service for Amazon EC2.

    Amazon EC2's simple web service interface allows you to obtain
    and configure capacity with minimal friction. It provides you
    with complete control of your computing resources and lets you
    run on Amazon's proven computing environment.
    """

    _metadata_version = '2009-04-04'
    """The version of metadata that will be consumed by the current
    metadata service."""

    _aliases = {
        HOST_NAME: ('local-hostname', 'hostname'),
        INSTANCE_ID: ('instance-id', ),
        PUBLIC_KEYS: ('public-keys', ),
    }
    """A dictionary that contains all the posible keywords for the required
    endpoints."""

    def __init__(self):
        super(EC2Service, self).__init__(base_url=CONF.ec2_metadata_base_url)
        self._enable_retry = True
        self._endpoints = {}

    @property
    def endpoints(self):
        """A dictionary which contains all the available endpoints."""
        if not self._endpoints:
            endpoints = self._get_cache_data('%s/meta-data/' %
                                             self._metadata_version,
                                             decode=True).splitlines()
            for endpoint in self._aliases:
                for alias in self._aliases[endpoint]:
                    if alias in endpoints:
                        self._endpoints[endpoint] = alias
                        break
                else:
                    LOG.debug("No endpoint available for %r", endpoint)
        return self._endpoints

    def _get_url(self, endpoint):
        """Prepare the URL for the required endpoint."""
        return "%(version)s/meta-data/%(endpoint)s" % {
            "version": self._metadata_version,
            "endpoint": self.endpoints[endpoint],
        }

    def _test_api(self):
        """Test if the EC2 serivce is responding properly."""
        try:
            self._get_cache_data('%s/meta-data/' % self._metadata_version,
                                 decode=True)
        except Exception as exc:
            LOG.exception(exc)
            LOG.debug('Metadata not found at URL %r',
                      CONF.ec2_metadata_base_url)
            return False
        else:
            LOG.debug('Metadata service %r responded properly.',
                      CONF.ec2_metadata_base_url)
            return True

    def load(self):
        """Load all the available information from the metadata service."""
        super(EC2Service, self).load()
        if CONF.ec2_add_metadata_private_ip_route:
            network.check_metadata_ip_route(CONF.ec2_metadata_base_url)
        return self._test_api()

    def get_host_name(self):
        """Get the hostname for the current instance.

        The hostname is the label assigned to the current instance used to
        identify it in various forms of electronic communication.
        """
        return self._get_cache_data(self._get_url(HOST_NAME), decode=True)

    def get_user_data(self):
        return self._get_cache_data(
            "%(version)s/user-data" % {"version": self._metadata_version}
        )

    def get_instance_id(self):
        """Get the identifier for the current instance.

        The instance identifier provides an unique way to address an
        instance into the current metadata provider.
        """
        return self._get_cache_data(self._get_url(INSTANCE_ID), decode=True)

    def get_public_keys(self):
        """Get a list of space-stripped strings as public keys.

        .. note::
            A first request to /public-keys will return all the available
            keys, each one per line in this form: "index=key-name". Then,
            based on the number of keys and their indexes, will follow
            requests like /public-keys/<index>/openssh-key which returns
            the actual content.
        """
        ssh_keys = []
        keys_info = self._get_cache_data(self._get_url(PUBLIC_KEYS),
                                         decode=True)
        for key_info in keys_info.splitlines():
            try:
                index, _ = key_info.split('=')
                ssh_key = self._get_cache_data(
                    '%(version)s/meta-data/public-keys/%(index)s/openssh-key' %
                    {'version': self._metadata_version, 'index': index},
                    decode=True)
                ssh_keys.append(ssh_key.strip())
            except ValueError:
                if key_info.startswith("ssh-rsa"):
                    ssh_keys.append(key_info.strip())
                else:
                    LOG.debug("Failed to process the following key %r",
                              key_info)

        return ssh_keys
