# Ansible Collection for NIFCLOUD

This is an unofficial Ansible collection to manage [NIFCLOUD](https://www.nifcloud.com/) resources.

## Installation

First of all, this collection requires dependencies.

```
pip3 install nifcloud==0.3.1
```

You can use `ansible-galaxy` CLI to install this collection.

```sh
ansible-galaxy collection install git+https://github.com/tottoto/ansible-collection-nifcloud.git
```

Or, you can also add an entry for this collection to `requirements.yml`.

```yaml
collections:
  - name: https://github.com/tottoto/ansible-collection-nifcloud.git
    type: git
```

Then you can install this collection by this command.

```sh
ansible-galaxy collection install -r requirements.yml
```

## Usage

The supported modules are located in [module directory](./plugins/modules/).
If there is `some_module_name.py` file in the module directory, the module FQCN is `tottoto.nifcloud.some_module_name`.

You can get the documentation for modules by `ansible-doc` CLI.
For example, you can use this command to get `tottoto.nifcloud.computing_key` documentation.

```sh
ansible-doc tottoto.nifcloud.computing_key
```
