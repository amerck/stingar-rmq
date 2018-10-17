# Copyright (C) 2018 Alexander Merck <merckedsec@gmail.com>
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
from datetime import datetime


class RawEvent:

    def __init__(self):
        pass

    @staticmethod
    def normalize(channel, uid, data):
        payload = json.loads(data)
        raw_event = {
            "ident": uid,
            "timestamp": datetime.utcnow(),
            "channel": channel,
            "payload": payload
        }
        return raw_event
