# Copyright (C) 2013 Johnny Vestergaard <jkv@unixcluster.dk>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import json
import re

from basenormalizer import BaseNormalizer

class DionaeaConnections(BaseNormalizer):
    channels = ('dionaea.connections',)

    def normalize_ip(self, ip):
        mat = re.match(r'[a-f0-9A-F:]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})$', ip)
        if mat:
            return mat.group(1)
        else:
            return ip

    def normalize(self, data, channel, submission_timestamp, ignore_rfc1918=True):
        o_data = self.parse_record_data(data)

        o_data['remote_host'] = self.normalize_ip(o_data['remote_host'])
        if ignore_rfc1918 and self.is_RFC1918_addr(o_data['remote_host']):
            return []

        # {
        #   "connection_type": "accept",
        #   "local_host": "::ffff:1.2.3.4",
        #   "connection_protocol": "httpd",
        #   "remote_port": 51912,
        #   "local_port": 80,
        #   "remote_hostname": "",
        #   "connection_transport": "tcp",
        #   "remote_host": "::ffff:4.5.6.7"
        # }

        return [
            {
                'session': {
                    'timestamp': submission_timestamp,
                    'source_ip': o_data['remote_host'],
                    'source_port': o_data['remote_port'],
                    'destination_port': o_data['local_port'],
                    'honeypot': 'dionaea',
                    'protocol': o_data['connection_protocol'],
                }
            },
        ]
