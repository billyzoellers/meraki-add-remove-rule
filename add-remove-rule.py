"""
Meraki group policy L7 firewall rule rule adder/remover

Billy Zoellers, 2020
"""
import sys
import meraki
from meraki.exceptions import APIError
from dynaconf.validator import ValidationError
from config import settings
from rich import print
from loguru import logger

def main():
  # Check for required settings
  try:
    settings.validators.validate()
  except ValidationError as err:
    logger.error(f'Missing required settings: {err}')
    sys.exit(1)
    
  # Dashboard API
  dashboard = meraki.DashboardAPI(api_key=settings.meraki_api_key, output_log=False, print_console=True, suppress_logging=True)

  # Find the specified organization
  org_name = settings.meraki.org_name
  try:
    orgs = dashboard.organizations.getOrganizations()
    org = next(org for org in orgs if org['name'] == org_name)
    logger.debug(f"Found organization '{org['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find organization named '{org_name}'")
    sys.exit(1)
  except APIError as err:
    logger.error(err)
    sys.exit(1)

  # Find the specified network
  net_name = settings.meraki.net_name
  try:
    nets = dashboard.organizations.getOrganizationNetworks(org['id']) 
    net = next(net for net in nets if net['name'] == net_name)
    logger.debug(f"Found network '{net['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find network named '{net_name}'")
    sys.exit(1)

  # Find the specified group policy (gp)
  gp_name = settings.meraki.grouppolicy_name
  try:
    gps = dashboard.networks.getNetworkGroupPolicies(net['id'])
    gp = next(gp for gp in gps if gp['name'] == gp_name)
    logger.debug(f"Found group policy '{gp['name']}'")
  except StopIteration:
    logger.exception(f"Unable to find group policy named '{gp_name}'")
    sys.exit(1)

  # Find the specified l7 rule
  l7FirewallRules = gp['firewallAndTrafficShaping']['l7FirewallRules']
  logger.debug(f"L7 firewall rule count: {len(l7FirewallRules)}")

  # Find the application category to add/remove
  l7_category = settings.meraki.l7_category
  try:
    app_categories = (dashboard.networks.getNetworkTrafficShapingApplicationCategories(net['id']))['applicationCategories']
    app_category = next(acat for acat in app_categories if acat['name'] == l7_category)
  except StopIteration:
    logger.exception(f"Unable to find app category named '{l7_category}'")
    sys.exit(1)

  # Remove the applications (keep top-level category only)
  del app_category['applications']
  logger.debug(f"Found app category '{app_category['name']}'")

  # Check if a rule for this app category already exists
  rule = any(rule for rule in l7FirewallRules if rule['value'] == app_category)
  if (rule):
    # Remove 1 or more rules for category
    logger.debug(f"Found existing rule for '{app_category['name']}'")
    remove_rules = [rule for rule in l7FirewallRules if rule['value'] == app_category]
    for rule in remove_rules:
      l7FirewallRules.remove(rule)
  else:
    # Add 1 rule for category
    logger.debug(f"Did not find existing rule for '{app_category['name']}'")
    add_rule = {'policy': 'deny', 'type': 'applicationCategory', 'value': app_category}
    l7FirewallRules.append(add_rule)

  # Upload new L7 rules to group policy
  logger.debug(f"New L7 firewall rule count: {len(l7FirewallRules)}")
  dashboard.networks.updateNetworkGroupPolicy(
    networkId=net['id'],
    groupPolicyId=gp['groupPolicyId'],
    firewallAndTrafficShaping=gp['firewallAndTrafficShaping']
  )
  
  # Message for user
  operation = 'removed' if rule else 'added'
  color = 'red' if rule else 'green'
  print(f"\n:heavy_check_mark: Firewall rule for [bold]{app_category['name']}[/bold] in [bold]{gp['name']}[/bold] has been [{color}]{operation}[/{color}]")

if __name__ == "__main__":
  main()