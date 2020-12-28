from os import environ


def module_core_args():
    return dict(
        access_key_id=dict(type='str', default=environ.get('NIFCLOUD_ACCESS_KEY_ID')),
        secret_access_key=dict(type='str', default=environ.get('NIFCLOUD_SECRET_ACCESS_KEY'), no_log=True),
        region=dict(type='str', default=environ.get('NIFCLOUD_DEFAULT_REGION'))
    )
