class ModuleDocFragment:
    DOCUMENTATION = '''
options:
  access_key_id:
    description: The NIFCLOUD access key id.
    required: false
    type: str
    env:
      - name: NIFCLOUD_ACCESS_KEY_ID
  secret_access_key:
    description: The NIFCLOUD secret access key.
    required: false
    type: str
    env:
      - name: NIFCLOUD_SECRET_ACCESS_KEY
    '''
