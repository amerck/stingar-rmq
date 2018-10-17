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

import logging
from datetime import datetime

from bson.objectid import ObjectId
from bson.errors import InvalidStringData
from pymongo import MongoClient

logger = logging.getLogger(__name__)


class StingarDB(object):

    def __init__(self, host, port, db_name):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.db = None

    def connect(self):
        logger.info('Connecting to mongodb, using "{0}" as database.'.format(self.db_name))
        conn = MongoClient(host=self.host, port=self.port)
        self.db = conn[self.db_name]
        self.ensure_index()

    def ensure_index(self):
        # self.db.raw_event.ensure_index([('normalized', 1), ('last_error', 1)], unique=False, background=True)
        self.db.auth_key.ensure_index('name', unique=False, background=True)
        self.db.auth_key.ensure_index('hostname', unique=False, background=True)
        self.db.auth_key.ensure_index('ip', unique=False, background=True)
        self.db.auth_key.ensure_index('honeypot', unique=False, background=True)
        self.db.auth_key.ensure_index('uuid', unique=True, background=False)
        self.db.auth_key.ensure_index('created_date', unique=False, background=True)
        self.db.auth_key.ensure_index('identifier', unique=False, background=True)
        self.db.auth_key.ensure_index('secret', unique=False, background=True)

    def insert_auth_key(self, entry):
        try:
            self.db.auth_key.insert_one(entry)
            del entry['_id']
            return entry
        except InvalidStringData:
            logger.error(
                'Failed to insert'
            )

    def get_auth_keys(self, uuid=None):
        query = {}
        if uuid:
            query = {"identifier": uuid}
        return self.db.auth_key.find(query)

    def get_secret(self, uuid):
        sensor = self.db.auth_key.find_one({"identifier": uuid})
        if sensor:
            return sensor['secret']
        return None

    def insert_event(self, entry):
        try:
            print("Inserting entry")
            self.db.raw_events.insert_one(entry)

            timestamp = datetime.utcnow()
            # Update honeypot event count
            self.db.counts.update({'identifier': entry['ident'],
                                   'date': timestamp.strftime('%Y%m%d')},
                                  {"$inc": {"event_count": 1}},
                                  upsert=True)

            # Update channel event count
            self.db.counts.update({'identifier': entry['channel'],
                                   'date': timestamp.strftime('%Y%m%d')},
                                  {"$inc": {"event_count": 1}},
                                  upsert=True)
        except InvalidStringData:
            logging.error(
                'Failed to insert'
            )

    def get_event_data(self, get_before_id, maximum=250, max_scan=10000):
        """Fetches unnormalized event items from the datastore.

        :param maximum: maximum number of entries to return
        :param max_scan: maximum number of mongo documents to scan
        :param get_before_id: only return entries which are below the value of this ObjectId
        :return: a list of dictionaries
        """

        data = list(self.db.raw_events.find({'_id': {'$lt': get_before_id}, 'normalized': False,
                                            'last_error': {'$exists': False}}, limit=maximum,
                                            sort=[('_id', -1)], max_scan=max_scan))
        return data

    def insert_normalized(self, ndata, event_id, identifier=None):
        assert isinstance(event_id, ObjectId)
        # ndata is a collection of dictionaries
        for item in ndata:
            # key = collection name, value = content
            for collection, document in item.items():
                if collection is 'url':
                    if 'extractions' in document:
                        self.db[collection].update({'url': document['url']},
                                                   {'$pushAll': {'extractions': document['extractions']},
                                                    '$push': {'event_ids': event_id}},
                                                   upsert=True)
                    else:
                        self.db[collection].update({'url': document['url']}, {'$push': {'event_ids': event_id}},
                                                   upsert=True)
                elif collection is 'file':
                    self.db[collection].update({'hashes.sha512': document['hashes']['sha512']},
                                               {'$set': document, '$push': {'event_ids': event_id}},
                                               upsert=True)
                elif collection is 'session':
                    document['event_id'] = event_id
                    if identifier:
                        document['identifier'] = identifier
                    self.db[collection].insert(document)
                elif collection is 'dork':
                    self.db[collection].update({'content': document['content'], 'type': document['type']},
                                               {'$set': {'lasttime': document['timestamp']},
                                                '$inc': {'count': document['count']}},
                                               upsert=True)
                elif collection is 'metadata':
                    if 'ip' in document and 'honeypot' in document:
                        query = {
                            'ip': document['ip'],
                            'honeypot': document['honeypot']
                        }
                        values = dict((k, v) for k, v in document.items() if k not in ['ip', 'honeypot'])
                        self.db[collection].update(query, {'$set': values}, upsert=True)
                else:
                    raise Warning('{0} is not a know collection type.'.format(collection))

        # if we end up here everything if ok - setting event entry to normalized
        self.db.raw_events.update({'_id': event_id}, {'$set': {'normalized': True},
                                  '$unset': {'last_error': 1, 'last_error_timestamp': 1}})

    def apiarist_set_errors(self, items):
        """
        Marks raw_events entries in the datastore as having errored while normalizing.

        "param items: a list of raw_event entries
        """
        for item in items:
            self.db.raw_events.update({'_id': item['_id']},
                                      {'$set': {'last_error': str(item['last_error']),
                                       'last_error_timestamp': item['last_error_timestamp']}
                                       })
