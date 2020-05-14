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


class Poller(NSOWrangler):
    def __init__(
        self,
        nso_server,
        nso_port,
        username,
        password
    ):
        """
            Pulls VPN session data from devices and can boot sessions.
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

        self.logger.info("Initializing Poller")

    def pullAllDeviceSessionData(self, devices):
        """
            Master function to pull VPN session data for multiple devices.

            :param devices: devices commands are intended for
            :type devices: list[str]

            :return: VPN session data for each device
            :rtype: dict[str] = dict
        """

        results = {}

        for device in devices:
            results[device] = self.pullDeviceSessionData(device)

        return results

    def pullDeviceSessionData(self, device):
        """
            Pull VPN session data for a device.

            :param device: device commands are intended for
            :type device: str

            :return: VPN session data - active, cumulative, and peak
            :rtype: dict[str] = int
        """

        self.logger.info(f"{device}:\tPulling device session data.")
        sessions = {
            'active': 0,
            'cumulative': 0,
            'peak': 0 
        }

        response = self.runCommandsOnDevice(device, ["show vpn-sessiondb"])

        if response is False:
            return sessions
        elif "AnyConnect Client" not in response:
            self.logger.info(f"{device}:\tNo session data.")
            return sessions

        session_stats = re.findall(r'\d+', response)
        sessions['active'] = int(session_stats[0])
        sessions['cumulative'] = int(session_stats[1])
        sessions['peak'] = int(session_stats[2])

        return sessions

    def clearAllDeviceSessionData(self, devices):
        """
            Master function to clear VPN session data for multiple devices.

            :param devices: devices commands are intended for
            :type devices: list[str]

            :return: success of clearing VPN session data for each device
            :rtype: dict[str] = bool
        """

        results = {}

        for device in devices:
            results[device] = self.clearDeviceSessionData(device)

        return results

    def clearDeviceSessionData(self, device):
        """
            Clear VPN session data for a device.

            :param device: device commands are intended for
            :type device: str

            :return: success of clearing VPN session data
            :rtype: bool
        """

        self.logger.info(f"{device}:\tClearing device session data.")

        response = self.runCommandsOnDevice(device, ["clear vpn-sessiondb statistics global"])

        if response is False:
            return False
        elif "INFO: Global session" not in response:
            self.logger.info(f"{device}:\tUnsuccesful in clearing session data.")
            return False

        return True

    def logoffUser(self, device, user):
        """
            Logs off a user session from a device.

            :param device: device commands are intended for
            :type device: str
            :param user: username of session being logged off
            :type user: str

            :return: success of logging off user session
            :rtype: bool
        """

        self.logger.info(f"{device}:\tLogging {user} off of {device}.")

        self.runCommandsOnDevice(device, f"vpn-sessiondb logoff name {user} noconfirm")

        if response is False:
            return False
        elif f'\"{user}\" logged off : 0' in response:
            self.logger.info(f"{device}:\tNo session active for {user}.")
            return False
        elif f'\"{user}\" logged off' not in response:
            self.logger.info(f"{device}:\tError trying to log out {user}.")
            return False

        return True

    def logoffAllUsersAllDevices(self, devices):
        """
            Master function for logging off all sessions from a list of devices.

            :param devices: devices commands are intended for
            :type device: list[str]

            :return: success of logging off user sessions from devices
            :rtype: dict[str] = bool
        """

        results = {}

        for device in devices:
            results[device] = self.logoffAllusers(device)

        return results

    def logoffAllUsers(self, device):
        """
            Logs off all sessions from a device.

            :param device: device commands are intended for
            :type device: list[str]

            :return: success of logging off user sessions from device
            :rtype: bool
        """

        self.logger.info(f"{device}:\tLogging all users off of {device}.")
        
        self.runCommandsOnDevice(device, f"vpn-sessiondb logoff all noconfirm")

        if response is False:
            return False
        
        return True


if __name__ == "__main__":
    import datetime
    import csv
    
    print("\n\npoller.py\n")

    NSO_SERVER = 'nso-server'
    NSO_PORT = '8888'
    USERNAME = 'user1'
    PASSWORD = 'pass1'

    DEVICES = ['vpn-device-1', 'vpn-device-2']

    poller = Poller(
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
            
            if filename == "sessions":
                writer.writerow(["device", "active", "cumulative", "peak"])

                for device in data:
                    writer.writerow([
                        device,
                        data[device]["active"],
                        data[device]["cumulative"],
                        data[device]["peak"]
                    ])

            if filename == "clear" or filename == "logoff":
                writer.writerow(["device", "result"])

                for device in data:
                    writer.writerow([device, data[device]])

    while True:
        print("\nPlease select the command you wish to perform:\n")
        print("\t1: Pull device session data")
        print("\t2: Clear device session data")
        print("\tKICK: Logoff all users from devices (with great power comes great responsibility)")
        print("\n(Optionally) append a -c (console) or -r (report)")
        command = input().strip().lower()

        print("Number crunching...")
        if "1" in command:
            result = poller.pullAllDeviceSessionData(DEVICES)
        elif "2" in command:
            result = poller.clearAllDeviceSessionData(DEVICES)
        elif "kick" in command:
            result = poller.logoffAllUsersAllDevices(DEVICES)
        else:
            print("Please enter a valid command.")
            continue

        if "c" in command:
            for device in result:
                print(f"{device}:\t{result[device]}")
        if "r" in command:
            if "1" in command:
                reportToCSV("sessions", result)
            elif "2" in command:
                reportToCSV("clear", result)
            elif "kick" in command:
                reportToCSV("logoff", result)
                