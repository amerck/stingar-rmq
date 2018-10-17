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

import pika

from events import HpEvents


class AMQPReceiver:

    def __init__(self, database, username, password, host='localhost'):
        self.database = database
        self.username = username
        self.password = password
        self.host = host

    def enable_registration_queue(self, ch, reg_queue='hp_reg'):
        ch.queue_declare(reg_queue)
        ch.basic_consume(self.handle_registration_request, queue=reg_queue)

    def enable_event_queue(self, ch, event_queue='hp_events'):
        ch.exchange_declare(exchange="honeypots",
                            exchange_type="topic")
        ch.queue_declare(queue=event_queue, exclusive=True)
        ch.queue_bind(exchange="honeypots",
                      queue=event_queue,
                      routing_key="cowrie.sessions")
        ch.basic_consume(self.handle_event_request,
                         queue=event_queue,
                         no_ack=True)

    def handle_registration_request(self, ch, method, props, body):
        reg_event = HpEvents().create_registration_event(body)
        reg_event = self.database.insert_auth_key(reg_event)
        ch.basic_publish(exchange='',
                         routing_key=props.reply_to,
                         properties=pika.BasicProperties(correlation_id=props.correlation_id),
                         body=json.dumps(reg_event, sort_keys=True, indent=4))
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def handle_event_request(self, ch, method, props, body):
        raw_event = HpEvents().create_raw_event(method.routing_key,
                                                props.correlation_id,
                                                body)
        self.database.insert_event(raw_event)

    def run(self):
        self.database.connect()

        credentials = pika.PlainCredentials(self.username, self.password)
        connection = pika.BlockingConnection(pika.ConnectionParameters(host=self.host, credentials=credentials))
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        self.enable_registration_queue(channel)
        self.enable_event_queue(channel)
        channel.start_consuming()
