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


import requests
import json
import logging
from logging.handlers import RotatingFileHandler


class NSOWrangler:
    def __init__(self, nso_server, nso_port, username, password, console=False):
        """
            API wrapper client for HTTPS calls to NSO.

            :param nso_server: device address of NSO server
            :type nso_server: str
            :param nso_port: port address of NSO server
            :type nso_port: str
            :param username: login username for NSO server
            :type username: str
            :param password: login password for NSO server
            :type password: str
            :param console: if True prints results to console
            :type console: bool
        """

        self.logger = self._initalizeLogs()
        self.logger.info("Initializing NSO Wrangler")

        self.nso_server = nso_server
        self.nso_port = nso_port
        self.username = username
        self.password = password
        self.base_api_url = f"https://{self.nso_server}:{self.nso_port}/restconf/operations/devices"

        self.console = console

    def _initalizeLogs(self):
        """
            Creates logging system for the NSO Wrangler class.
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

    def runCommandsOnDevices(self, devices, commands, success_message="", failure_message=""):
        """
            Master function to run commands on multiple devices.

            :param devices: hostnames of devices commands are intended for
            :type devices: list[str]
            :param commands: commands for device separated into a list
            :type commands: list[str]
            :param success_message: specific output from device that denotes success
            :type success_message: str
            :param failure_message: specific output from device that denotes failure
            :type failure_message: str

            :return: response from NSO for each device
            :rtype: dict[str] = str
        """

        results = {}

        for device in devices:
            results[device] = self.runCommandsOnDevice(device, commands, success_message, failure_message)
        
        return results

    def runCommandsOnDevice(self, device, commands, success_message="", failure_message=""):
        """
            Utilizes NSO REST API to run commands on devices.

            :param device: hostname of device commands are intended for
            :type device: str
            :param commands: commands for device separated into a list
            :type commands: list[str]
            :param success_message: specific output from device that denotes success
            :type success_message: str
            :param failure_message: specific output from device that denotes failure
            :type failure_message: str

            :return: response from NSO for device
            :rtype: str
        """
        
        self.logger.info(f"{device}:\tPerforming the following commands: {commands}.")

        command_string = '\n'.join(commands)
        url = f"{self.base_api_url}/device={device}/live-status/tailf-ned-cisco-asa-stats:exec/any"
        payload = json.dumps({ "input": { "args": command_string }})
        headers = { "Content-Type": "application/yang-data+json" }

        try:
            response = requests.request(
                "POST",
                url=url,
                auth=(self.username, self.password),
                headers=headers,
                data=payload,
                verify=False
            )
        except Exception as error:
            self.logger.error(f"{device}:\t{error}")
            return False       

        try:
            device_data = json.loads(response.text)

            if "errors" in device_data:
                self.logger.error(f"{device}:\t{device_data['errors']}")
                if self.console:
                  print(f"{device}: {device_data['errors']}\n")
                return False
            
            output = device_data["tailf-ned-cisco-asa-stats:output"]["result"]
            if self.console:
                print(f"{device}: {output}\n")

            if failure_message and failure_message in output:
                return False
            if success_message and success_message in output:
                return output

            return output

        except Exception as error:
            self.logger.error(f"{device}:\t{error}")
            return False


if __name__ == "__main__":
    print("\nnso_wrangler.py\n")

    NSO_SERVER = 'nso-server'
    NSO_PORT = '8080'
    USERNAME = 'user1'
    PASSWORD = 'pass1'

    DEVICES = ['vpn-device-1', 'vpn-device-2']
    COMMANDS = ['show run route']

    nso_wrangler = NSOWrangler(
        nso_server=NSO_SERVER,
        nso_port=NSO_PORT,
        username=USERNAME,
        password=PASSWORD,
        console=True
    )

    nso_wrangler.runCommandsOnDevices(DEVICES, COMMANDS)
