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

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.plugins.common import base
from oslo_log import log as oslo_logging

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)

CONF = cloudbaseinit_conf.CONF
LOG = oslo_logging.getLogger(__name__)


class FinalizePlugin(base.BasePlugin):
    execution_stage = base.PLUGIN_STAGE_FINALIZE

    def execute(self, service, shared_data):
        on_finalize = service.on_finalize()
        if (on_finalize):
            on_finalize()
            return base.PLUGIN_EXECUTION_DONE, False
        else:
            LOG.debug("Service does not implement finalize action.")
