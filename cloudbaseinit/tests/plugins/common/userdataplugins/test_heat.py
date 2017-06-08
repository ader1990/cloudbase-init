# Copyright 2013 Cloudbase Solutions Srl
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

import base64
import os
import sys
import unittest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from cloudbaseinit import conf as cloudbaseinit_conf
from cloudbaseinit.plugins.common.userdataplugins import heat

CONF = cloudbaseinit_conf.CONF


class HeatUserDataHandlerTests(unittest.TestCase):

    def setUp(self):
        self._heat = heat.HeatPlugin()

    @mock.patch('os.path.exists')
    @mock.patch('os.makedirs')
    @mock.patch('os.path.dirname')
    def test_check_heat_config_dir(self, mock_dirname, mock_makedirs,
                                   mock_exists):
        mock_exists.return_value = False
        fake_path = mock.sentinel.fake_path
        fake_dir = mock.sentinel.fake_dir
        mock_dirname.return_value = fake_dir

        self._heat._check_dir(file_name=fake_path)

        mock_dirname.assert_called_once_with(fake_path)
        mock_exists.assert_called_once_with(fake_dir)
        mock_makedirs.assert_called_once_with(fake_dir)

    @mock.patch('cloudbaseinit.plugins.common.userdatautils'
                '.execute_user_data_script')
    @mock.patch('cloudbaseinit.plugins.common.userdataplugins.heat'
                '.HeatPlugin._check_dir')
    @mock.patch('cloudbaseinit.utils.encoding.write_file')
    def _test_process(self, mock_write_file, mock_check_dir,
                      mock_execute_user_data_script, filename, payloads=False,
                      payload_base_64=False):
        mock_part = mock.MagicMock()
        mock_part.get_filename.return_value = filename
        part_payload = mock.Mock()
        if payloads is True:
            if payload_base_64:
                part_payload = base64.b64encode(b'payload data')
                mock_part.__getitem__.return_value = 'base64'
            elif sys.version_info < (3, 0):
                part_payload = filename.decode()
        mock_part.get_payload.return_value = part_payload
        response = self._heat.process(mock_part)

        path = os.path.join(CONF.heat_config_dir, filename)
        mock_check_dir.assert_called_once_with(path)
        mock_part.get_filename.assert_called_with()
        if payload_base_64:
            mock_write_file.assert_called_once_with(
                path, base64.b64decode(part_payload))
        else:
            mock_write_file.assert_called_once_with(path, part_payload)

        if filename == self._heat._heat_user_data_filename:
            if payload_base_64:
                mock_execute_user_data_script.assert_called_with(
                    base64.b64decode(part_payload))
            else:
                mock_execute_user_data_script.assert_called_with(part_payload)
            self.assertEqual(mock_execute_user_data_script.return_value,
                             response)
        else:
            self.assertTrue(response is None)

    def test_process(self):
        self._test_process(filename=self._heat._heat_user_data_filename)

    def test_process_payload(self):
        self._test_process(filename=self._heat._heat_user_data_filename,
                           payloads=True)

    def test_process_content_other_data(self):
        self._test_process(filename='other data')

    def test_process_payload_base64(self):
        self._test_process(filename=self._heat._heat_user_data_filename,
                           payloads=True, payload_base_64=True)
