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


class AmunEvents(BaseNormalizer):
    channels = ('amun.events',)

    def normalize(self, data, channel, submission_timestamp, ignore_rfc1918=True):
        o_data = self.parse_record_data(data)

        if ignore_rfc1918 and self.is_RFC1918_addr(o_data['attackerIP']):
            return []

        session = {
            'timestamp': submission_timestamp,
            'source_ip': o_data['attackerIP'],
            'source_port': int(o_data['attackerPort']),
            'destination_ip': o_data['victimIP'],
            'destination_port': int(o_data['victimPort']),
            'honeypot': 'amun'
        }

        protocol = super(AmunEvents, self).port_to_service(int(o_data['victimPort']))
        if protocol is not None:
            session['protocol'] = protocol

        relations = {'session': session}
        return [relations]
