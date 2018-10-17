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

from basenormalizer import BaseNormalizer


class Snort(BaseNormalizer):
    channels = ('snort.alerts',)

    def normalize(self, data, channel, submission_timestamp, ignore_rfc1918=True):
        o_data = self.parse_record_data(data)

        if ignore_rfc1918 and self.is_RFC1918_addr(o_data['source_ip']):
            return []

        session = {
            'timestamp': submission_timestamp,
            'source_ip': o_data['source_ip'],
            'destination_ip': o_data['destination_ip'],
            
            'honeypot': 'snort',
            'protocol': o_data['proto'],
            
            'snort': {
                'header': o_data['header'],
                'signature': o_data['signature'],
                'classification': o_data['classification'],
                'priority': o_data['priority'],
            },
            'sensor': o_data['sensor'] # UUID
        }

        # ICMP will have no ports
        if 'destination_port' in o_data:
            session['destination_port'] = o_data['destination_port']
        if 'source_port' in o_data:
            session['source_port'] = o_data['source_port']

        return [{'session': session},]
