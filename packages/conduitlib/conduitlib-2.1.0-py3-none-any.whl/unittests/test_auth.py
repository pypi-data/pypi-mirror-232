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
from pathlib import Path
from shutil import rmtree
import yaml
from conduitlib import auth

if __name__ == '__main__':
    unittest.main()

etc_dir = Path('etc')
secrets_file_path = etc_dir / 'local' / 'secrets.yaml'


class TestSetup(unittest.TestCase):
    def setUp(self):
        rmtree(etc_dir, ignore_errors=True)
        (etc_dir / 'local').mkdir(parents=True)

        auth.auth_dir = None
        auth.secret_path = None
        auth.secrets = None

    def test_no_secrets(self):
        self.assertFalse(secrets_file_path.exists())
        auth.setup(etc_dir)
        self.assertFalse(secrets_file_path.exists())

    def test_encrypted_secrets(self):
        self.assertFalse(secrets_file_path.exists())

        secrets = {
            's1': '$1$derp',
            's2': '$1$herp',
        }

        with secrets_file_path.open('w') as f:
            yaml.safe_dump(secrets, f)

        auth.setup(etc_dir)

        with secrets_file_path.open() as f:
            contents = yaml.safe_load(f)
            self.assertEqual(secrets, contents)

    def test_unencrypted_secrets(self):
        self.assertFalse(secrets_file_path.exists())

        secrets = {
            's1': 'derp',
            's2': 'herp',
        }

        with secrets_file_path.open('w') as f:
            yaml.safe_dump(secrets, f)

        auth.setup(etc_dir)

        with secrets_file_path.open() as f:
            contents = yaml.safe_load(f)
            self.assertEqual(len(secrets), len(contents))
            for secret_id, secret_text in contents.items():
                self.assertIn(secret_id, secrets)
                self.assertTrue(secret_text.startswith('$1$'))

    def test_one_unencrypted_secret(self):
        self.assertFalse(secrets_file_path.exists())

        secrets = {
            's1': 'derp',
            's2': '$1$herp',
        }

        with secrets_file_path.open('w') as f:
            yaml.safe_dump(secrets, f)

        auth.setup(etc_dir)

        with secrets_file_path.open() as f:
            contents = yaml.safe_load(f)
            self.assertEqual(len(secrets), len(contents))
            for secret_id, secret_text in contents.items():
                self.assertIn(secret_id, secrets)
                self.assertTrue(secret_text.startswith('$1$'))


class TestGetSecret(unittest.TestCase):
    def create_file(self):
        self.assertFalse(secrets_file_path.exists())

        secrets = {
            's1': 'derp',
            's2': 'herp',
        }

        with secrets_file_path.open('w') as f:
            yaml.safe_dump(secrets, f)

    def setUp(self):
        rmtree(etc_dir, ignore_errors=True)
        (etc_dir / 'local').mkdir(parents=True)

        auth.auth_dir = None
        auth.secret_path = None
        auth.secrets = None

    def test_nominal_1(self):
        self.create_file()

        auth.setup(etc_dir)

        with auth.get_secret('s1') as secret:
            self.assertEqual('derp', secret)

    def test_nominal_2(self):
        self.create_file()

        auth.setup(etc_dir)

        with auth.get_secret('s2') as secret:
            self.assertEqual('herp', secret)

    def test_invalid(self):
        self.create_file()

        auth.setup(etc_dir)

        with self.assertRaises(auth.NoSecretFoundException):
            with auth.get_secret('s3'):
                pass

    def test_invalid_no_file(self):
        auth.setup(etc_dir)

        with self.assertRaises(auth.NoSecretFoundException):
            with auth.get_secret('s1'):
                pass

    def test_not_setup(self):
        with self.assertRaises(auth.AuthNotSetupException):
            with auth.get_secret('s1'):
                pass
