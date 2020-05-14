# Poller
*Pulls VPN Session Data to Monitor ASA Device Health*

Child class which inherits from NSO Wrangler.

## To Run
```
python poller.py
```

The following constants are declared in `"__main__"` of [poller.py](./poller.py):

```
NSO_SERVER = 'nso-server'  # NSO server address
NSO_PORT = '8888'          # NSO server port
USERNAME = 'user1'         # username for NSO
PASSWORD = 'pass1'         # password for NSO

# List of device hostnames within NSO to poll VPN session data
DEVICES = ['vpn-device-1', 'vpn-device-2']
```

Instantiation of the `Poller` class:

```
poller = Poller(
    nso_server=NSO_SERVER,
    nso_port=NSO_PORT,
    username=USERNAME,
    password=PASSWORD
)
```

This program gives the ability to pull or clear session data as well as logoff users.
```
# pulls VPN session data
poller.pullAllDeviceSessionData(DEVICES)

# clears VPN session data
poller.clearAllDeviceSessionData(DEVICES)

# disconnects all VPN sessions
poller.logoffAllUsersAllDevices(DEVICES)
```

[poller.py](./poller.py) gives a rundown on how to utilize the `Poller` class and output the information in various formats (`console` or `.csv`).

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
├── poller.py (main program and a code explanation on how to use the API)
├── logs (all logging for poller.py is sent here unless specified otherwise)
├── reports (all reports for poller.py are sent here)
```

## Authors & Maintainers
- Drew Taylor <dretaylo@cisco.com>

## License
This project is licensed to you under the terms of the [Cisco Sample
Code License](./LICENSE).
