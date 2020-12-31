import re

import nifcloud
from ansible.plugins.inventory import BaseInventoryPlugin

DOCUMENTATION = '''
  name: nifcloud_computing
  plugin_type: inventory
  short_description: NIFCLOUD conputing inventory source
  description:
    - NIFCLOUD conputing inventory source
  requirements:
    - nifcloud
  extends_documentation_fragment:
    - tottoto.nifcloud.nifcloud_credentials
  options:
    plugin:
      description: Token that ensures this is a source file for the plugin.
      choices: ['nifcloud_computing']
    regions:
      description: A list of regions in which to describe NIFCLOUD computing instances.
      type: list
      default: []
    tagging_by_instance_name:
      description: A list of rules to group instances by the instance name.
      type: list
      default: []
'''

EXAMPLES = '''
  # Minimal example
  plugin: tottoto.nifcloud.nifcloud_computing
  regions:
    - jp-east-2
  tagging_by_instance_name:
    - name: test
      pattern: '.*test.*'
'''


class InventoryModule(BaseInventoryPlugin):

    NAME = 'tottoto.nifcloud.nifcloud_computing'

    def verify_file(self, path):
        if super().verify_file(path):
            if path.endswith(('nifcloud_computing.yml', 'nifcloud_computing.yaml')):
                return True
        return False

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path)

        self._read_config_data(path)

        access_key_id = self.get_option('access_key_id')
        secret_access_key = self.get_option('secret_access_key')
        regions = self.get_option('regions')

        tags = self.get_option('tagging_by_instance_name')
        for tag in tags:
            self.inventory.add_group(tag['name'])

        for region in regions:
            self.inventory.add_group(region)

            nifcloud_client = nifcloud.session.get_session().create_client(
                'computing',
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                region_name=region
            )
            response = nifcloud_client.describe_instances()

            hosts = [{
                'id': rs['InstancesSet'][0]['InstanceUniqueId'],
                'name': rs['InstancesSet'][0]['InstanceId'],
                'ip_address': rs['InstancesSet'][0]['IpAddress'],
                'state': rs['InstancesSet'][0]['InstanceState']['Name']
            } for rs in response['ReservationSet']]

            for host in hosts:
                if host['state'] == 'running':
                    # grouping by the instance id
                    self.inventory.add_group(host['id'])
                    self.inventory.add_host(
                        host['ip_address'], group=host['id'])

                    # grouping by the instance name
                    self.inventory.add_group(host['name'])
                    self.inventory.add_host(
                        host['ip_address'], group=host['name'])

                    # grouping by the region
                    self.inventory.add_host(host['ip_address'], group=region)

                    # grouping by the pattern of the instance name
                    for tag in tags:
                        if re.match(tag['pattern'], host['name']):
                            self.inventory.add_host(host['ip_address'], group=tag['name'])
