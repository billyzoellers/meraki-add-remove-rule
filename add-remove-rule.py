"""
Meraki group policy L7 firewall rule rule adder/remover

Billy Zoellers, 2020
"""
import meraki
from app_helper import find_org, find_net, find_gp, find_app_category, user_message, check_settings
from config import settings
from rich import print
from loguru import logger

def main():
  check_settings(settings)
    
  # Dashboard API
  dashboard = meraki.DashboardAPI(api_key=settings.meraki_api_key, output_log=False, print_console=True, suppress_logging=True)

  # Find the specified organization, network, group policy
  org = find_org(dashboard, settings.meraki.org_name)
  net = find_net(dashboard, org['id'], settings.meraki.net_name)
  gp = find_gp(dashboard, net['id'], settings.meraki.grouppolicy_name)

  # Find the specified l7 rule
  l7FirewallRules = gp['firewallAndTrafficShaping']['l7FirewallRules']
  logger.debug(f"L7 firewall rule count: {len(l7FirewallRules)}")

  # Find the application category to add/remove
  app_category = find_app_category(dashboard, net['id'], settings.meraki.l7_category)
  del app_category['applications']

  # Check if a rule for this app category already exists
  rule_exists = any(rule for rule in l7FirewallRules if rule['value'] == app_category)
  if (rule_exists):
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
  print(user_message(app_category['name'], gp['name'], not(rule_exists)))
  
if __name__ == "__main__":
  main()