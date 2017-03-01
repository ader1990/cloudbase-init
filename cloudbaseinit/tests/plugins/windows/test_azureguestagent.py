# Copyright (c) 2017 Cloudbase Solutions Srl
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

import importlib
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.plugins.common import base
from cloudbaseinit.tests import testutils

CONF = cloudbaseinit_conf.CONF
MODPATH = "cloudbaseinit.plugins.windows.azureguestagent"


class AzureGuestAgentPluginTest(unittest.TestCase):

    def setUp(self):
        self.mock_wmi = mock.MagicMock()
        self._moves_mock = mock.MagicMock()
        patcher = mock.patch.dict(
            "sys.modules",
            {
                "wmi": self.mock_wmi,
                "six.moves": self._moves_mock
            }
        )
        patcher.start()
        self.addCleanup(patcher.stop)
        self._azureguestagent = importlib.import_module(MODPATH)
        self._azureagentplugin = self._azureguestagent.AzureGuestAgentPlugin()
        self.snatcher = testutils.LogSnatcher(MODPATH)

    def test_check_delete_service(self):
        mock_osutils = mock.Mock()
        mock_service_name = mock.sentinel.name
        self._azureagentplugin._check_delete_service(mock_osutils,
                                                     mock_service_name)
        mock_osutils.check_service_exists.assert_called_once_with(
            mock_service_name)
        mock_osutils.get_service_status.assert_called_once_with(
            mock_service_name)
        mock_osutils.stop_service.assert_called_once_with(mock_service_name,
                                                          wait=True)
        mock_osutils.delete_service.assert_called_once_with(mock_service_name)

    @mock.patch(MODPATH + ".AzureGuestAgentPlugin._check_delete_service")
    def test_remove_agent_services(self, mock_check_delete_service):
        mock_osutils = mock.Mock()
        mock_service_name = mock.sentinel.name
        expected_logs = ["Stopping and removing any existing Azure guest "
                         "agent services"]
        with self.snatcher:
            self._azureagentplugin._remove_agent_services(mock_osutils)
        self.assertEqual(self.snatcher.output, expected_logs)
        self.assertEqual(mock_check_delete_service.call_count, 3)

    @mock.patch("shutil.rmtree")
    @mock.patch("os.path.exists")
    @mock.patch("os.getenv")
    def test_remove_azure_dirs(self, mock_os_getenv,
                               mock_exists, mock_rmtree):
        mock_rmtree.side_effect = (None, Exception)
        with self.snatcher:
            self._azureagentplugin._remove_azure_dirs()
        self.assertEqual(self.snatcher.output[1], "")

    def test_set_registry_vm_type(self):
        pass

    def test_set_registry_ga_params(self):
        pass

    def test_configure_rd_agent(self):
        pass

    @mock.patch(MODPATH + ".AzureGuestAgentPlugin._run_logman")
    def test_stop_event_trace(self, mock_run_logman):
        pass

    @mock.patch(MODPATH + ".AzureGuestAgentPlugin._run_logman")
    def test_delete_event_trace(self, mock_run_logman):
        pass

    def test_run_logman(self):
        mock_osutils = mock.Mock()

    @mock.patch(MODPATH + ".AzureGuestAgentPlugin._stop_event_trace")
    def test_stop_ga_event_traces(self, mock_stop_event_trace):
        pass

    @mock.patch(MODPATH + ".AzureGuestAgentPlugin._stop_event_trace")
    def test_delete_ga_event_traces(self, mock_stop_event_trace):
        pass

    def test_get_guest_agent_source_path(self):
        pass

    def _test_execute(self):
        mock_service = mock.Mock()

    def test_get_os_requirements(self):
        expected_res = ('win32', (6, 1))
        res = self._azureagentplugin.get_os_requirements()
        self.assertEqual(res, expected_res)
