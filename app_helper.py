import meraki
import sys
from meraki import APIError
from loguru import logger
from dynaconf.validator import ValidationError

def user_message(app_category_name, group_policy_name, added_rule):
  operation = 'added' if added_rule else 'removed'
  color = 'green' if added_rule else 'red'
  
  return f"\n:heavy_check_mark: Firewall rule for [bold]{app_category_name}[/bold] in [bold]{group_policy_name}[/bold] has been [{color}]{operation}[/{color}]"

def find_org(dashboard, org_name):
  try:
    orgs = dashboard.organizations.getOrganizations()
    org = next(org for org in orgs if org['name'] == org_name)
    logger.info(f"Found organization '{org['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find organization named '{org_name}'")
    sys.exit(1)
  except APIError as err:
    logger.error(err)
    sys.exit(1)

  return org

def find_net(dashboard, org_id, net_name):
  try:
    nets = dashboard.organizations.getOrganizationNetworks(org_id) 
    net = next(net for net in nets if net['name'] == net_name)
    logger.info(f"Found network '{net['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find network named '{net_name}'")
    sys.exit(1)

  return net

def find_gp(dashboard, net_id, gp_name):
  try:
    gps = dashboard.networks.getNetworkGroupPolicies(net_id)
    gp = next(gp for gp in gps if gp['name'] == gp_name)
    logger.info(f"Found group policy '{gp['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find group policy named '{gp_name}'")
    sys.exit(1)

  return gp

def find_app_category(dashboard, net_id, ac_name):
  try:
    app_categories = (dashboard.networks.getNetworkTrafficShapingApplicationCategories(net_id))['applicationCategories']
    app_category = next(acat for acat in app_categories if acat['name'] == ac_name)
    logger.info(f"Found app category '{app_category['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find app category named '{ac_name}'")
    sys.exit(1)
  
  return app_category

def check_settings(settings):
  try:
    settings.validators.validate()
  except ValidationError as err:
    logger.error(f'Missing required settings: {err}')
    sys.exit(1)