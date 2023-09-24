__version__ = '0.1.4'

import re
import logging
import requests

from akips.exceptions import AkipsError

# Logging configuration
logger = logging.getLogger(__name__)


class AKIPS:
    # Class to handle interactions with AKiPS API

    def __init__(self, server, username='api-ro', password=None, verify=True):
        ''' Connect to the AKiPS instance '''
        self.server = server
        self.username = username
        self.password = password
        self.verify = verify
        self.session = requests.Session()

        if (not verify):
            requests.packages.urllib3.disable_warnings()

    def get_devices(self):
        ''' Pull a list of key fields for all devices in akips '''
        params = {
            'cmds': 'mget text * sys /ip.addr|SNMPv2-MIB.sysName|SNMPv2-MIB.sysDescr|SNMPv2-MIB.sysLocation/',
        }
        text = self.akips_get(params=params)
        if text:
            data = {}
            # Data comes back as 'plain/text' type so we have to parse it
            lines = text.split('\n')
            for line in lines:
                match = re.match(r'^(\S+)\s(\S+)\s(\S+)\s=\s(.*)$', line)
                if match:
                    if match.group(1) not in data:
                        # Populate a default entry for all desired fields
                        data[match.group(1)] = {
                            'ip4addr': '',
                            'SNMPv2-MIB.sysName': '',
                            'SNMPv2-MIB.sysDescr': '',
                            'SNMPv2-MIB.sysLocation': '',
                        }
                    # Save this attribute value to data
                    data[match.group(1)][match.group(3)] = match.group(4)
            logger.debug("Found {} devices in akips".format(len(data.keys())))
            return data
        return None

    def get_device(self, name):
        ''' Pull the entire configuration for a single device '''
        # params = {
        #     'cmds': 'mget * {} * *'.format(name),
        # }
        pass

    def get_device_by_ip(self, ipaddr, use_cache=True):
        ''' Search for a device by an alternate IP address
        This makes use of a special site script and not the normal api '''
        # params = {
        #     'function': 'web_find_device_by_ip',
        #     'ipaddr': ipaddr
        # }
        # section = '/api-script/'
        pass

    def get_unreachable(self):
        ''' Pull a list of unreachable IPv4 ping devices '''
        # params = {
        #     'cmds': 'mget * * * /PING.icmpState|SNMP.snmpState/ value /down/',
        # }
        pass

    def get_group_membership(self):
        ''' Pull a list of device to group memberships '''
        # params = {
        #     'cmds': 'mgroup device *',
        # }
        pass

    def get_maintenance_mode(self):
        ''' Pull a list of devices in maintenance mode '''
        # params = {
        #     'cmds': 'mget * * any group maintenance_mode',
        # }
        pass

    def set_maintenance_mode(self, device_name, mode='True'):
        ''' Set maintenance mode on or off for a device '''
        # params = {
        #     'function': 'web_manual_grouping',
        #     'type': 'device',
        #     'group': 'maintenance_mode',
        #     'device': device_name
        # }
        pass

    def get_status(self, device='*', child='*', attribute='*'):
        ''' Pull the status values we are most interested in '''
        pass

    def get_events(self, type='all', period='last1h'):
        ''' Pull a list of events.  Command syntax:
            mget event {all,critical,enum,threshold,uptime}
            time {time filter} [{parent regex} {child regex}
            {attribute regex}] [profile {profile name}]
            [any|all|not group {group name} ...] '''

        params = {
            'cmds': 'mget event {} time {}'.format(type, period)
        }
        text = self.akips_get(params=params)
        if text:
            data = []
            lines = text.split('\n')
            for line in lines:
                match = re.match(r'^(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s(\S+)\s(.*)$', line)
                if match:
                    entry = {
                        'epoch': match.group(1),
                        'parent': match.group(2),
                        'child': match.group(3),
                        'attribute': match.group(4),
                        'type': match.group(5),
                        'flags': match.group(6),
                        'details': match.group(7),
                    }
                    data.append(entry)
            logger.debug("Found {} events of type {} in akips".format(len(data), type))
            return data
        return None

    def akips_get(self, section='/api-db/', params=None, timeout=30):
        ''' Call HTTP GET against the AKiPS server '''
        server_url = 'https://' + self.server + section
        params['username'] = self.username
        params['password'] = self.password

        try:
            r = self.session.get(server_url, params=params, verify=self.verify, timeout=timeout)
            r.raise_for_status()
        except requests.exceptions.HTTPError as errh:
            logger.error(errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            logger.error(errc)
            raise
        except requests.exceptions.Timeout as errt:
            logger.error(errt)
            raise
        except requests.exceptions.RequestException as err:
            logger.error(err)
            raise

        # AKiPS can return a raw error message if something fails
        if re.match(r'^ERROR:', r.text):
            logger.error("Web API request failed: {}".format(r.text))
            raise AkipsError(message=r.text)
        else:
            # AKiPS signaled a success
            return r.text
