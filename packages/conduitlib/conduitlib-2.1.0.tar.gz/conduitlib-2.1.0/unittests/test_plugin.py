# Copyright 2021 Software Factory Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from conduitlib import plugin

if __name__ == '__main__':
    unittest.main()


class MyPlugin(plugin.Plugin):
    def execute(self, data=None):
        self.logger.info('I am a plugin!!!')
        return data


class MyTrigger(plugin.Trigger):
    def run(self):
        self.logger.info('I am a trigger!!!')


class TestPlugin(unittest.TestCase):
    def test_execute_not_implemented(self):
        class MyBadPlugin(plugin.Plugin):
            pass

        my_plugin = MyBadPlugin('cool_workflow', 1111)

        with self.assertRaises(NotImplementedError):
            my_plugin.execute()

    def test_logs(self):
        my_plugin = MyPlugin('cool_workflow', 1111)

        with self.assertLogs(None, level='INFO') as cm:
            my_plugin.execute()

        expected = ['INFO:unittests.test_plugin.MyPlugin:[cool_workflow:1111] I am a plugin!!!']

        self.assertEqual(expected, cm.output)


class TestTrigger(unittest.TestCase):
    def test_execute_not_implemented(self):
        class MyBadTrigger(plugin.Trigger):
            pass

        my_trigger = MyBadTrigger('cool_workflow')

        with self.assertRaises(NotImplementedError):
            my_trigger.run()

    def test_logs(self):
        my_trigger = MyTrigger('cool_workflow')

        with self.assertLogs(None, level='INFO') as cm:
            my_trigger.run()

        expected = ['INFO:unittests.test_plugin.MyTrigger:[cool_workflow] I am a trigger!!!']

        self.assertEqual(expected, cm.output)
