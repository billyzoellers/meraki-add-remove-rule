## Meraki Add/Remove rule
Select an organization, network, group policy, and Layer 7 application category. If the Layer 7 category exists as a deny rule, remove it. If it does not exist, add it.

## Getting started
1. `pip install -r requirements.txt`
2. Define settings in `settings.toml` and `secrets.toml` to run the app
3. Go!

### settings.toml
```
[meraki]
org_name = 'your Meraki org name'
net_name = 'your Meraki network name'
grouppolicy_name = 'your Meraki group policy name'
l7_category = 'Meraki L7 category name>'
```

### secrets.toml
```
meraki_api_key='your_meraki_api_key'
```