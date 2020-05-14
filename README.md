# NSO Wrangler
*NSO REST API Wrapper for Running Commands on Devices*

This repo contains an API designed to make it easier to perform device commands using NSO's REST API.

I've included specific examples on how to utilize `NSO Wrangler` for your network's specific needs by using it as a parent class, although the `NSO Wrangler` class can work as a standalone.
- [Poller](./poller/) - Pulls VPN session data to monitor ASA device health.
- [Split Tunnel Manager](./split-tunnel-manager/) - Audits, manages, and clears FQDN split tunnels on ASAs.

These programs also provide a good template for network automation regardless if the developer has access to an NSO server. Simply replace the `NSO Wrangler` API with an alternative networking automation library such as Ansible or Paramiko.

Where `NSO Wrangler` fits:
```
Network Devices <-> NSO Wrangler <-> Network Automation Programs
```

Swapping out `NSO Wrangler` for an alternative:
```
Network Devices <-> Ansible <-> Network Automation Programs
```

*Please note that the libraries Ansible, Paramiko, etc. do not provide a 1:1 replacement with NSO. [NSO](https://developer.cisco.com/docs/nso/) is a network orchestration platform designed to manage devices, audit configuration, provide transaction history, and much more.*

## Installation
This code requires Python 3 and has been tested with Python 3.7.7.

```
git clone git@github.com:CiscoDevNet/nso-wrangler.git
cd nso-wrangler/
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## To Run
```
python nso_wrangler.py
```

The following constants are declared in `"__main__"` of [nso_wrangler.py](./nso_wrangler.py):

```
NSO_SERVER = 'nso-server'  # NSO server address
NSO_PORT = '8888'          # NSO server port
USERNAME = 'user1'         # username for NSO
PASSWORD = 'pass1'         # password for NSO

# List of device hostnames within NSO
DEVICES = ['vpn-device-1', 'vpn-device-2']
# Commands to be run on devices
COMMANDS = ['show vpn-sessiondb', 'show vpn load-balancing']
```

Instantiation of the NSO Wrangler class:

```
nso_wrangler = NSOWrangler(
    nso_server=NSO_SERVER,
    nso_port=NSO_PORT,
    username=USERNAME,
    password=PASSWORD,
    console=True
)
```

Runs the given commands on the devices (declared above):

```
nso_wrangler.runCommandsOnDevices(DEVICES, COMMANDS)
```

Please view the READMEs for [poller](./poller/README.md) and [split-tunnel-manager](./split-tunnel-manager/README.md) for further expansion on how to utilize NSO Wrangler.

## [Poller](./poller/)
Pulls and clears VPN session DB data. Also can disconnect VPN sessions.

## [Split Tunnel Manager](./split-tunnel-manager/)
Audits, updates, and clears FQDN split tunneling configuration on VPN headends.

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
├── nso_wrangler.py (main program and a code explanation on how to use the API)
├── logs (all logging for nso_wrangler.py is sent here unless specified otherwise)
├── poller (example program)
|   ├── poller.py (main program and a code explanation on how to use the API)
|   ├── reports (all reports for poller.py are sent here)
|   └── logs (all logging for poller.py is sent here)
├── split-tunnel-manager (example program)
|   ├── split_tunnel_manager.py (main program and a code explanation on how to use the API)
|   ├── reports (all reports for split_tunnel_manager.py are sent here)
|   └── logs (all logging for poller.py is sent here)
```

## Authors & Maintainers
- Drew Taylor <dretaylo@cisco.com>

## License
This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
