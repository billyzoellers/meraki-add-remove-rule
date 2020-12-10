
from dynaconf import Dynaconf, Validator

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=['settings.toml', '.secrets.toml'],
    validators=[
      Validator('meraki_api_key', must_exist=True),
      Validator('meraki.org_name', must_exist=True),
      Validator('meraki.net_name', must_exist=True),
      Validator('meraki.grouppolicy_name', must_exist=True),
      Validator('meraki.l7_category', must_exist=True),
    ],
)

# `envvar_prefix` = export envvars with `export DYNACONF_FOO=bar`.
# `settings_files` = Load this files in the order.
