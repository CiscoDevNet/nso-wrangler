"""NSO Wrangler API Program.
Copyright (c) 2020 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

__author__ = "Drew Taylor"
__email__ = "dretaylo@cisco.com"
__version__ = "0.1.1"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"


import logging
from logging.handlers import RotatingFileHandler
import re
import sys
sys.path.append('..')

from nso_wrangler import NSOWrangler


class SplitTunnelManager(NSOWrangler):
    def __init__(
        self,
        nso_server,
        nso_port,
        username,
        password
    ):
        """
            Audits, manages, and clears FQDN split tunneling on ASAs.
            Utilizes NSOWrangler to run commands on devices.

            :param nso_server: device address of NSO server
            :type nso_server: str
            :param nso_port: port address of NSO server
            :type nso_port: str
            :param username: login username for NSO server
            :type username: str
            :param password: login password for NSO server
            :type password: str
        """

        super().__init__(
            nso_server=nso_server,
            nso_port=nso_port,
            username=username,
            password=password,
            console=False
        )

        self.logger.info("Initializing Split Tunnel Manager")

    def _initalizeLogs(self):
        """
            Creates logging system for the Poller class.
            Will prevent NSOWrangler from writing its own logs.
            Logs are contained within the file "./logs/poller-debug.log".
        """

        logger_file_handler = RotatingFileHandler(filename="./logs/poller-debug.log", maxBytes=2000000, backupCount=5)
        logger_file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter('%(asctime)s:\t%(levelname)s:\t%(threadName)s:\t%(funcName)s:\t\t%(message)s')
        logger_file_handler.setFormatter(formatter)

        logging.captureWarnings(True)

        logger = logging.getLogger(__name__)
        warnings_logger = logging.getLogger("py.warnings")

        logger.addHandler(logger_file_handler)
        logger.setLevel(logging.DEBUG)
        warnings_logger.addHandler(logger_file_handler)

        return logger

    def auditDevices(self, devices, group_policy, exclude_domains, include_domains):
        """
            Master function to audit FQDN split tunneling for multiple devices.

            :param devices: devices commands are intended for
            :type devices: list[str]
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param exclude_domains: domains that should be split tunneled (exclude)
            :type exclude_domains: list[str]
            :param include_domains: domains that should not be split tunneled (include)
            :type include_domains: list[str]

            :return: FQDN split tunneling data for each device
            :rtype: dict[str] = dict
        """

        results = {}

        for device in devices:
            results[device] = self.auditDevice(device, group_policy, exclude_domains, include_domains)

        return results

    def auditDevice(self, device, group_policy, exclude_domains, include_domains):
        """
            Audits FQDN split tunneling for a device by looking at what's being excluded/included.

            :param device: device commands are intended for
            :type device: str
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param exclude_domains: domains that should be split tunneled (exclude)
            :type exclude_domains: list[str]
            :param include_domains: domains that should not be split tunneled (include)
            :type include_domains: list[str]

            :return: FQDN split tunneling data for a device
            :rtype: dict[str] = dict
        """

        results = {}

        if exclude_domains:
            self.logger.info(f"{device}:\tAuditting exclude domains")
            results['exclude'] = self.auditPolicyConfig(device, group_policy, exclude_domains, "exclude")

        if include_domains:
            self.logger.info(f"{device}:\tAuditting include domains")
            results['include'] = self.auditPolicyConfig(device, group_policy, include_domains, "include")

        return results

    def auditPolicyConfig(self, device, group_policy, domains, split_policy):
        """
            Audits FQDN split tunneling for a device.

            :param device: device commands are intended for
            :type device: str
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param domains: domains that should be in configuration
            :type domains: list[str]
            :param split_policy: "include" or "exclude"
            :type split_policy: str

            :return: exclude or include FQDN split tunneling data for a device
            :rtype: dict[str] = bool/list
        """

        checks = {
            'webvpn': False,
            'group_policy': False,
            'domains': [],
            'domains_missing': [],
            'domains_extra': [],
        }

        response = self.runCommandsOnDevice(device, [f"show run | include dynamic-split-{split_policy}-domains"])

        if response is False:
            return checks

        for line in response.split('\r\n'):
            if f"anyconnect-custom-attr dynamic-split-{split_policy}-domains" in line:
                checks['webvpn'] = True
            if f"anyconnect-custom dynamic-split-{split_policy}-domains value {group_policy.lower()}_{split_policy}" in line:
                checks['group_policy'] = True
            if f"anyconnect-custom-data dynamic-split-{split_policy}-domains {group_policy.lower()}_{split_policy}" in line:
                checks['domains'] += re.findall(r"([^\s,]+)(?=,)", line)

        device_domains = set(checks['domains'])
        audit_domains = set(domains)

        for domain in audit_domains:
            if domain not in device_domains:
                checks['domains_missing'].append(domain)

        for domain in device_domains:
            if domain not in audit_domains:
                checks['domains_extra'].append(domain)

        checks['domains'].sort()

        return checks

    def updateDevices(self, devices, group_policy, exclude_domains, include_domains):
        """
            Master function to update FQDN split tunneling for multiple devices.

            :param devices: devices commands are intended for
            :type devices: list[str]
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param exclude_domains: domains that should be split tunneled (exclude)
            :type exclude_domains: list[str]
            :param include_domains: domains that should not be split tunneled (include)
            :type include_domains: list[str]

            :return: success of updating FQDN split tunneling data for each device
            :rtype: dict[str] = dict
        """

        results = {}

        for device in devices:
            results[device] = self.updateDevice(device, group_policy, exclude_domains, include_domains)

        return results

    def updateDevice(self, device, group_policy, exclude_domains, include_domains):
        """
            Updates FQDN split tunneling for a device by updating what's being excluded/included.

            :param device: device commands are intended for
            :type device: str
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param exclude_domains: domains that should be split tunneled (exclude)
            :type exclude_domains: list[str]
            :param include_domains: domains that should not be split tunneled (include)
            :type include_domains: list[str]

            :return: success of updating FQDN split tunneling data for a device
            :rtype: dict[str] = bool
        """

        results = {}

        if exclude_domains:
            self.logger.info(f"{device}:\tUpdating exclude domains")
            results['exclude'] = self.updatePolicyConfig(device, group_policy, exclude_domains, "exclude")

        if include_domains:
            self.logger.info(f"{device}:\tUpdating include domains")
            results['include'] = self.updatePolicyConfig(device, group_policy, include_domains, "include")

        return results

    def updatePolicyConfig(self, device, group_policy, domains, split_policy):
        """
            Updates FQDN split tunneling for a device.

            :param device: device commands are intended for
            :type device: str
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param domains: domains that should be in configuration
            :type domains: list[str]
            :param split_policy: "include" or "exclude"
            :type split_policy: str

            :return: success of updating the exclude or include FQDN split tunneling data for a device
            :rtype: bool
        """

        config = [
            "config t",
            "webvpn",
            f"anyconnect-custom-attr dynamic-split-{split_policy}-domains description FQDN split tunneling {split_policy}",
            "exit",
        ]

        domain_data_template = f"anyconnect-custom-data dynamic-split-{split_policy}-domains {group_policy.lower()}_{split_policy} "
        domain_list = ""

        for domain in domains:
            new_length = len(domain_list) + len(domain) + 1

            if new_length < 421:
                domain_list += f"{domain},"
            else:
                config.append(domain_data_template + domain_list)
                domain_list = f"{domain},"
                
        if domain_list:
            config.append(domain_data_template + domain_list)

        config += [
            f"group-policy {group_policy} attributes",
            f"anyconnect-custom dynamic-split-{split_policy}-domains value {group_policy.lower()}_{split_policy}",
            "exit",
            "write"
        ]

        response = self.runCommandsOnDevice(device, config)

        return True if response else False

    def clearDevices(self, devices, group_policy):
        """
            Master function to clear FQDN split tunneling for multiple devices.

            :param devices: devices commands are intended for
            :type devices: list[str]
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str

            :return: success of clearing FQDN split tunneling data for each device
            :rtype: dict[str] = dict
        """

        results = {}

        for device in devices:
            results[device] = self.clearDevice(device, group_policy)

        return results

    def clearDevice(self, device, group_policy):
        """
            Clears FQDN split tunneling for a device by clearing what's being excluded/included.

            :param device: device commands are intended for
            :type device: str
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str

            :return: success of clearing FQDN split tunneling data for a device
            :rtype: dict[str] = bool
        """

        results = { 'exclude': False, 'include': False }
        
        self.logger.info(f"{device}:\tClearing exclude domains")
        results['exclude'] = self.clearPolicyConfig(device, group_policy, "exclude")

        self.logger.info(f"{device}:\tClearing include domains")
        results['include'] = self.clearPolicyConfig(device, group_policy, "include")

        return results

    def clearPolicyConfig(self, device, group_policy, split_policy):
        """
            Clears FQDN split tunneling for a device.

            :param device: device commands are intended for
            :type device: str
            :param group_policy: group policy where FQDN split tunneling is being applied
            :type group_policy: str
            :param split_policy: "include" or "exclude"
            :type split_policy: str

            :return: success of clearing the exclude or include FQDN split tunneling data for a device
            :rtype: bool
        """

        config = [
            "config t",
            f"group-policy {group_policy} attributes",
            f"no anyconnect-custom dynamic-split-{split_policy}-domains",
            "exit",
            f"no anyconnect-custom-data dynamic-split-{split_policy}-domains {group_policy.lower()}_{split_policy}",
            "write",
        ]

        response = self.runCommandsOnDevice(device, config)

        return True if response else False


if __name__ == "__main__":
    import datetime
    import csv

    print("\n\nsplit_tunnel_manager.py\n")

    NSO_SERVER = 'nso-server'
    NSO_PORT = '8888'
    USERNAME = 'user1'
    PASSWORD = 'pass1'

    DEVICES = ['vpn-device-1', 'vpn-device-2']
    GROUP_POLICY = 'DEFAULT_GROUP_POLICY'
    EXCLUDE_DOMAINS = ['webex.com', 'netflix.com', 'youtube.com']
    INCLUDE_DOMAINS = ['cisco.com']

    split_tunnel_manager = SplitTunnelManager(
        nso_server=NSO_SERVER,
        nso_port=NSO_PORT,
        username=USERNAME,
        password=PASSWORD
    )

    def reportToCSV(filename, data):
        date = datetime.datetime.now()
        csv_filename = f"{filename}_{date.month}-{date.day}-{date.year}_{date.hour}-{date.minute}.csv"
        with open(f"./reports/{csv_filename}", "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            
            if filename == "audit":
                writer.writerow(["device", "policy", "audit", "domains"])

                for device in data:
                    writer.writerow([device])

                    for policy in data[device]:
                        writer.writerow(['', policy])

                        domains_missing = data[device][policy]['domains_missing'] if data[device][policy]['domains_missing'] else ['N/A']
                        domains_extra = data[device][policy]['domains_extra'] if data[device][policy]['domains_extra'] else ['N/A']

                        writer.writerow(['', '', 'missing', *domains_missing])
                        writer.writerow(['', '', 'extra', *domains_extra])

                writer.writerow("")
                writer.writerow(['exclude domains', *exclude_domains])
                writer.writerow(['include domains', *include_domains])

            if filename == "update" or filename == "clear":
                writer.writerow(["device", "success"])

                for device in data:
                    writer.writerow([device, data[device]['exclude'] and data[device]['include']])

    while True:
        print("\nPlease select the command you wish to perform:\n")
        print("\t1: Audit the domains on devices")
        print("\t2: Update the domains on devices")
        print("\t3: Clear the domains on devices")
        print("\n(Optionally) append a -c (console) or -r (report)")
        command = input().strip().lower()

        print("Number crunching...")
        if "1" in command:
            result = split_tunnel_manager.auditDevices(
                devices=DEVICES,
                group_policy=GROUP_POLICY,
                exclude_domains=EXCLUDE_DOMAINS,
                include_domains=INCLUDE_DOMAINS
            )
        elif "2" in command:
            result = split_tunnel_manager.updateDevices(
                devices=DEVICES,
                group_policy=GROUP_POLICY,
                exclude_domains=EXCLUDE_DOMAINS,
                include_domains=INCLUDE_DOMAINS
            )
        elif "3" in command:
            result = split_tunnel_manager.clearDevices(
                devices=DEVICES,
                group_policy=GROUP_POLICY
            )
        else:
            print("Please enter a valid command.")
            continue

        if "c" in command:
            for device in result:
                print(f"{device}:\t{result[device]}")
        if "r" in command:
            if "1" in command:
                reportToCSV("audit", result)
            if "2" in command:
                reportToCSV("update", result)
            if "3" in command:
                reportToCSV("clear", result)
