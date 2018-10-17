import sys
import json
import argparse
import requests
import pika


class AMQPRegistrationClient(object):

    def __init__(self, username, password, host='localhost', port=5672):
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host, port=port, credentials=credentials))
        self.channel = self.connection.channel()
        self.channel.basic_consume(self.on_response, no_ack=True, queue='amq.rabbitmq.reply-to')
        self.response = None

    def on_response(self, ch, method, props, body):
        self.response = body

    def register(self, reg_msg):
        self.channel.basic_publish(exchange='',
                                   routing_key='hp_reg',
                                   properties=pika.BasicProperties(
                                       reply_to='amq.rabbitmq.reply-to',
                                   ),
                                   body=json.dumps(reg_msg))
        while self.response is None:
            self.connection.process_data_events()
        return self.response


def generate_registration(name, hostname, ip_addr, honeypot):
    reg_msg = {"name": name,
               "hostname": hostname,
               "ip": ip_addr,
               "honeypot": honeypot
               }
    return reg_msg


def main():
    parser = argparse.ArgumentParser(description="Honeypot Registration")
    parser.add_argument("--name", default=False, required=True, help="Honeypot name")
    parser.add_argument("--hostname", default=False, required=True, help="Honeypot hostname")
    parser.add_argument("--honeypot", default=False, required=True, help="Honeypot type")
    parser.add_argument("--ip_addr", default=False, required=True, help="Honeypot IP address")
    parser.add_argument("--rabbitmq", action='store_true', default=False, required=False,
                        help="Use RabbitMQ for honeypot communication")
    parser.add_argument("--amqp_user", default=False, required=False, help="RabbitMQ username for use with "
                                                                           "--rabbitmq option")
    parser.add_argument("--amqp_pass", default=False, required=False, help="RabbitMQ password for use with "
                                                                           "--rabbitmq option")
    parser.add_argument("--regkey", default=False, required=False, help="API registration key for use with "
                                                                        "--webapi option")
    parser.add_argument("--reghost", default=False, required=True, help="Hostname of registration server")
    parser.add_argument("--regport", default=False, required=True, help="Listening port of registration server")
    args = parser.parse_args()

    name = args.name
    hostname = args.hostname
    honeypot = args.honeypot
    ip_addr = args.ip_addr
    reghost = args.reghost
    regport = args.regport
    amqp_user = args.amqp_user
    amqp_pass = args.amqp_pass

    reg_msg = generate_registration(name, hostname, ip_addr, honeypot)

    if not (amqp_user or amqp_pass):
        sys.stderr("Must specify both RabbitMQ username and password.\n")
        return -1
    client = AMQPRegistrationClient(amqp_user, amqp_pass, host=reghost, port=regport)
    response = client.register(reg_msg)
    print("%s" % response)
    return 0


if __name__ == "__main__":
    main()