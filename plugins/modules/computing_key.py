#!/usr/bin/python
# -*- coding: utf-8 -*-

import uuid

import botocore
import nifcloud
from ansible.module_utils.basic import AnsibleModule

DOCUMENTATION = '''
---
module: computing_key
short_description: create or delete a computing key pair
description:
    - create or delete a computing key pair.
options:
    name:
        description:
            - Name of the key pair.
        required: true
        type: str
    password:
        description:
            - Password of the key pair.
            - Required when (state=present) and exclusive with key_material
        type: str
    key_material:
        description:
            - Publick key material that is encoded by base64.
            - Required when (state=present) and exclusive with password
    force:
        description:
            - Allow overwrite of already existing key pair when key is changed.
        required: false
        default: true
    state:
        description:
            - create or delete a key pair.
        required: false
        choices: [present, absent]
        default: present
        type: str
    description:
        description:
            - Description of the key pair.
        required: false
        default: ''
        type: str

requirements: [nifcloud]
author:
    - tottoto (@tottoto)
'''

EXAMPLES = '''
# Pass in a message
- tottoto.nifcloud.computing_key:
    name: mytestkey1
    password: mytestkeypass1
    description: mytestkeydescription1
'''

RETURN = '''
changed:
  description: whether the key pair was created/updated/deleted
  returned: always
  type: bool
  sample: true
msg:
  description: short message describing the action taken
  returned: always
  type: str
  sample: key pair created
key:
  description: details of the key pair
  returned: always
  type: complex
  containes:
    name:
      description: name of the key pair
      returned: when state is present
      type: str
      sample: mysamplekey
    fingerprint:
      description: fingerprint of the key
      returned: when a new key pair is created
      sample: 5a:2e:0e:8b:0e:4a:ff:cb:dc:ed:40:d0:11:1c:89:4d
    private_key:
      description: base64 encoded private key of the created key pair
      returned: whe a new key pair is created by NIFCLOUD
      type: str
      sample: (base64 encoded string)
'''


def extract_key_data(key):
    key_data = {
        'name': key['KeyName'],
        'fingerprint': key['KeyFingerprint']
    }
    if 'KeyMaterial' in key:
        key_data.update({'private_key': key['KeyMaterial']})
    return key_data


def find_key_pair(nifcloud_client, name):
    try:
        key = nifcloud_client.describe_key_pairs(KeyName=[name])['KeySet'][0]
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'Client.InvalidParameterNotFound.KeyPair':
            key = None
        else:
            raise
    return key


def create_key_pair(module, nifcloud_client, name, password, description):
    found_key = find_key_pair(nifcloud_client, name)
    if found_key is None:
        if not module.check_mode:
            response = nifcloud_client.create_key_pair(
                KeyName=name,
                Password=password,
                Description=description
            )
            key_data = extract_key_data(response)
        else:
            key_data = None
        module.exit_json(changed=True, key=key_data, msg='key pair created')
    else:
        key_data = extract_key_data(found_key)
        module.exit_json(changed=False, key=key_data, msg='key pair already exists')


def delete_key_pair(module, nifcloud_client, name):
    found_key = find_key_pair(nifcloud_client, name)
    if found_key is not None:
        if not module.check_mode:
            nifcloud_client.delete_key_pair(KeyName=name)
            key_data = None
        else:
            key_data = extract_key_data(found_key)
        module.exit_json(changed=True, key=key_data, msg='key pair deleted')
    else:
        module.exit_json(changed=False, key=None, msg='key did not exist')


def import_key_pair(module, nifcloud_client, name, key_material, description, force):
    found_key = find_key_pair(nifcloud_client, name)
    if found_key is None:
        if not module.check_mode:
            response = nifcloud_client.import_key_pair(
                KeyName=name,
                PublicKeyMaterial=key_material,
                Description=description
            )
            key_data = extract_key_data(response)
        else:
            key_data = None
        module.exit_json(changed=True, key=key_data, msg='key pair created')
    elif force:
        new_fingerprint = get_key_fingerprint(
            module, nifcloud_client, key_material
        )
        if found_key['KeyFingerprint'] != new_fingerprint:
            if not module.check_mode:
                nifcloud_client.delete_key_pair(KeyName=name)
                response = nifcloud_client.import_key_pair(
                    KeyName=name,
                    PublicKeyMaterial=key_material,
                    Description=description
                )
                key_data = extract_key_data(response)
            else:
                key_data = None
            module.exit_json(changed=True, key=key_data, msg='key pair updated')
    key_data = extract_key_data(found_key)
    module.exit_json(changed=False, key=key_data, msg='key pair already exist')


def get_key_fingerprint(module, nifcloud_client, key_material):
    name_in_use = True
    while name_in_use is not None:
        random_name = 'ansible' + str(uuid.uuid4()).replace('-', '')[:-7]
        name_in_use = find_key_pair(nifcloud_client, random_name)
    tmp_key = nifcloud_client.import_key_pair(
        KeyName=random_name,
        PublicKeyMaterial=key_material,
        Description=''
    )
    key_data = extract_key_data(tmp_key)
    nifcloud_client.delete_key_pair(KeyName=random_name)
    return tmp_key['KeyFingerprint']


def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        password=dict(type='str'),
        key_material=dict(type='str'),
        force=dict(type='bool', default=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        description=dict(type='str', default='')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        mutually_exclusive=[('password', 'key_material')],
        required_if=[('state', 'present', ('password', 'key_material'), True)],
        supports_check_mode=True
    )

    nifcloud_client = nifcloud.session.get_session().create_client('computing')

    state = module.params['state']
    name = module.params['name']

    if state == 'absent':
        delete_key_pair(module, nifcloud_client, name)
    elif state == 'present':
        description = module.params['description']
        key_material = module.params['key_material']
        if key_material is not None:
            force = module.params['force']
            import_key_pair(module, nifcloud_client, name, key_material, description, force)
        else:
            password = module.params['password']
            create_key_pair(module, nifcloud_client, name, password, description)


def main():
    run_module()


if __name__ == '__main__':
    main()
