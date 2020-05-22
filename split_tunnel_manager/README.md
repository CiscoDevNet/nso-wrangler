# Split Tunnel Manager
*Audits, Updates, and Clears FQDN Split Tunneling Configuration on VPN Headends*

Child class which inherits from NSO Wrangler.

To read more about FQDN split tunneling on the ASA OS click [here](https://www.cisco.com/c/en/us/support/docs/security/anyconnect-secure-mobility-client/215383-asa-anyconnect-dynamic-split-tunneling.html).

## To Run
```
python split_tunnel_manager.py
```

The following constants are declared in `"__main__"` of [split_tunnel_manager.py](./split_tunnel_manager.py):

```
NSO_SERVER = 'nso-server'  # NSO server address
NSO_PORT = '8888'          # NSO server port
USERNAME = 'user1'         # username for NSO
PASSWORD = 'pass1'         # password for NSO

# List of device hostnames within NSO to poll VPN session data
DEVICES = ['vpn-device-1', 'vpn-device-2']

# Group policy that FQDN split tunnels are associated with
GROUP_POLICY = 'DEFAULT_GROUP_POLICY'

# FQDN split tunnel exclude domains
EXCLUDE_DOMAINS = ['webex.com', 'netflix.com', 'youtube.com']

# FQDN split tunnel include domains
INCLUDE_DOMAINS = ['cisco.com']
```

Instantiation of the `Split Tunnel Manager` class:

```
split_tunnel_manager = SplitTunnelManager(
    nso_server=NSO_SERVER,
    nso_port=NSO_PORT,
    username=USERNAME,
    password=PASSWORD
)
```

This program gives the ability to audit, update, or clear FQDN split tunneling data on VPN headends.
```
# audits FQDN split tunneling
split_tunnel_manager.auditDevices(
    devices=DEVICES,
    group_policy=GROUP_POLICY,
    exclude_domains=EXCLUDE_DOMAINS,
    include_domains=INCLUDE_DOMAINS
)

# updates FQDN split tunneling
split_tunnel_manager.updateDevices(
    devices=DEVICES,
    group_policy=GROUP_POLICY,
    exclude_domains=EXCLUDE_DOMAINS,
    include_domains=INCLUDE_DOMAINS
)

# clears FQDN split tunneling
split_tunnel_manager.clearDevices(
    devices=DEVICES,
    group_policy=GROUP_POLICY
)
```

[split_tunnel_manager.py](./split_tunnel_manager.py) gives a rundown on how to utilize the `Split Tunnel Manager` class and output the information in various formats (`console` or `.csv`).

## Technologies & Frameworks Used

**Cisco Products & Services:**

- [Network Services Orchestrator (NSO)](https://developer.cisco.com/docs/nso/)
- [Cisco ASA OS Software](https://www.cisco.com/c/en/us/products/security/adaptive-security-appliance-asa-software/index.html)
- [AnyConnect VPN Client](https://www.cisco.com/c/en/us/products/security/anyconnect-secure-mobility-client/index.html)

**Tools & Frameworks:**

- Python 3.7
- `requests` module

## File Structure
```
.
├── split_tunnel_manager.py (main program and a code explanation on how to use the API)
├── logs (all logging for split_tunnel_manager.py is sent here unless specified otherwise)
├── reports (all reports for split_tunnel_manager.py are sent here)
```

## Authors & Maintainers
- Drew Taylor <dretaylo@cisco.com>

## License
This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
