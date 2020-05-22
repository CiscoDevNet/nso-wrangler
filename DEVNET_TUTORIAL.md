# Cisco DevNet's Cisco Network Services Orchestrator Sandbox
The purpose of this tutorial is to showcase NSO's capabilities as well as how `NSO Wrangler` uses NSO's RESTCONF API to run commands on devices similar to other programs such as Ansible, Paramiko, etc. Using the package [`Split Tunnel Manager`](./split_tunnel_manager/) as an example, we can build off the API that `NSO Wrangler` provides to create network automation.

## Startup and Connection
1. Login to [devnet.cisco.com](devnetsandbox.cisco.com)
3. Click "Reserve" for "Cisco Network Services Orchestrator"
4. Wait for the sandbox environment to spin up (approx. 15 minutes)
5. Once the sandbox environment is finished setting up, an email will be sent with instructions on how to connect to the lab environment
6. Use Cisco AnyConnect to connect to the host address and port using the credentials specified
7. Once the VPN session is established, you are now succesfully connected to the lab environment

## Accessing NSO
1. Return to the DevNet Sandbox for NSO with the network topology diagram
2. Click "Instructions"
  - The "Network Devices" tab gives you a list of the networking devices available within your network, these devices are directly accessible via ssh/telnet
  - The "Cisco Network Services Orchestrator" tab gives you an overview of NSO as well as additional links to learn more about NSO
3. There are three ways to access the NSO server:
  - GUI through Web Browser
  - SSH to the Linux box and then enter the NSO console through bash
  - SSH directly into NSO (the method we will be using for this tutorial)
4. Open terminal/powershell/PUTTY and SSH directly into NSO using the command given, ex: `ssh -p 2024 developer@10.10.20.49`
5. Enter the password designated
6. If you see the prompt `developer@ncs#`, you have succesfully accessed NSO
7. Today we are going to be using NSO to access the device `edge-firewall01`, the ASA in our network topology
8. Try entering in the command `show running-config devices edge-firewall01`, this will show the configuration of `edge-firewall01` since the last "sync" with the network device
9. To "re-sync" the network device with NSO run this command `devices device edge-firewall01 sync-from`
8. Everything you can do on the console is available via GUI and vice versa, enter "?" at any point to see what commands you can currently enter

## Using NSO Wrangler with NSO
1. Open up terminal and change your current directory to `nso-wrangler/`
2. Pull up the python interactive shell by entering in `python` (this may vary for users, if you do not have the interactive shell you can always stick to modifying the `nso_wrangler.py` file directly)
3. In the python shell enter the following the commands:
```
from nso_wrangler import NSOWrangler

nso_wrangler = NSOWrangler(
    '10.10.20.49',  # IP of NSO server in sandbox (given)
    '443',          # Restconf API port for NSO server in sandbox (given)
    'developer',    # Username for NSO server in sandbox (given)
    'C1sco12345'    # Password for NSO server in sandbox (given)
)

nso_wrangler.runCommandsOnDevice('edge-firewall01', ['show run route'])
# nso_wrangler.runCOmmandsOnDevice('edge-firewall01', ['show run route']).split('\r\n')   # prettify
```

4. Using the credentials given, this runs the `show run route` command on `edge-firewall01` and returns the output to the shell

5. This works on more than just show commands, lets give our firewall a group policy:
```
nso_wrangler.runCommandsOnDevice('edge-firewall01', ['config t', 'group-policy DEFAULT_GROUP_POLICY internal'])
```

6. Now if you telnet into `edge-firewall01` to verify:
```
edge-firewall01# show run group-policy 
group-policy DEFAULT_GROUP_POLICY internal
```
For the less networking inclined (like myself):
```
telnet 10.10.20.171

Trying 10.10.20.171...
Connected to 10.10.20.171.
Password: cisco

edge-firewall01> en
Password: cisco

edge-firewall01#
```

7. Go back to the NSO console and check `edge-firewall01` to see if it has the group-policy:
```
developer@ncs# show running-config devices device edge-firewall01 | include group-policy
developer@ncs# 
```

8. It doesn't, you need to sync first:
```
developer@ncs# devices device edge-firewall01 sync-from  
result true
developer@ncs#
```
9. Now check again:
```
developer@ncs# show running-config devices device edge-firewall01 | include group-policy
  group-policy DEFAULT_GROUP_POLICY internal
developer@ncs# 
```

## Beyond NSO Wrangler with Split Tunnel Manager
`NSO Wrangler` is great and all for running commands on multiple devices at a time, however with network automation we can take that one step further and use `NSO Wrangler` as an API tool for a management task such as managing FQDN split tunneling (unfortunately I am unable to showcase the `Poller` class as it requires VPN connections which our lab ASA device lacks).

1. Lets import `SplitTunnelManager` into our python interactive shell:
```
from split_tunnel_manager.split_tunnel_manager import SplitTunnelManager
```

2. Instantiate the class similar to `NSOWrangler`
```
split_tunnel_manager = SplitTunnelManager(
    '10.10.20.49',  # IP of NSO server in sandbox (given)
    '443',          # Restconf API port for NSO server in sandbox (given)
    'developer',    # Username for NSO server in sandbox (given)
    'C1sco12345'    # Password for NSO server in sandbox (given)
)
```

3. Declare the domains to be split tunneled/exclusively not split tunneled:
```
EXCLUDE_DOMAINS = ['webex.com', 'netflix.com', 'youtube.com']
INCLUDE_DOMAINS = ['cisco.com']
```

4. Lets audit our group policy `DEFAULT_GROUP_POLICY` which currently resides on `edge-firewall01`:
```
split_tunnel_manager.auditDevice('edge-firewall01', 'DEFAULT_GROUP_POLICY', EXCLUDE_DOMAINS, INCLUDE_DOMAINS)
```
This will output (although maybe a little less clean):
```
{
  'exclude': {
    'webvpn': False,  # checks the webvpn for correct config
    'group_policy': False,  # checks the group policy for correct config
    'domains': [],
    'domains_missing': ['youtube.com', 'netflix.com', 'webex.com'],
    'domains_extra': []
  },
  'include': {
    'webvpn': False,
    'group_policy': False,
    'domains': [],
    'domains_missing': ['cisco.com'],
    'domains_extra': []
  }
}
```

6. Time to update the FQDN split tunnels for our `DEFAULT_GROUP_POLICY`:
```
split_tunnel_manager.updateDevice('edge-firewall01', 'DEFAULT_GROUP_POLICY', EXCLUDE_DOMAINS, INCLUDE_DOMAINS)
```
`True` designates the update was succesful:
```
{'exclude': True, 'include': True}
```

7. Lets run our audit to make sure we're in compliance now:
```
split_tunnel_manager.auditDevice('edge-firewall01', 'DEFAULT_GROUP_POLICY', EXCLUDE_DOMAINS, INCLUDE_DOMAINS)
```
Nice! Everything seems to be there!
```
{
  'exclude': {
    'webvpn': True,
    'group_policy': True,
    'domains': ['netflix.com', 'webex.com', 'youtube.com'],
    'domains_missing': [],
    'domains_extra': []
  },
  'include': {
    'webvpn': True,
    'group_policy': True,
    'domains': ['cisco.com'],
    'domains_missing': [],
    'domains_extra': []
  }
}
```

8. To sanity check that our FQDN split tunneling configuration is on the device, let's manually check it using telnet again:
```
edge-firewall01# show run | include dynamic-split
 anyconnect-custom-attr dynamic-split-exclude-domains description FQDN split tunneling exclude
 anyconnect-custom-attr dynamic-split-include-domains description FQDN split tunneling include
anyconnect-custom-data dynamic-split-exclude-domains default_group_policy_exclude webex.com,netflix.com,youtube.com,
anyconnect-custom-data dynamic-split-include-domains default_group_policy_include cisco.com,
 anyconnect-custom dynamic-split-exclude-domains value default_group_policy_exclude
 anyconnect-custom dynamic-split-include-domains value default_group_policy_include
```

9. Finished! To build out this network automation further, we can have a master list (or DB) of the include and exclude domains on a server and have this script pull the domain info from there. Furthermore, we can set up chron jobs to run audits on our network devices to make sure they're compliant and whenever our include and exclude domains are updated, our split tunnel manager package will automatically update all devices in the network.

## Authors & Maintainers
- Drew Taylor <dretaylo@cisco.com>

## License
This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
