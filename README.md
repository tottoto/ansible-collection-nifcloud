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
