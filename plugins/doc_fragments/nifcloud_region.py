class ModuleDocFragment:
    DOCUMENTATION = '''
options:
  region:
    description: The NIFCLOUD region.
    required: false
    type: str
    env:
      - name: NIFCLOUD_DEFAULT_REGION
    '''
