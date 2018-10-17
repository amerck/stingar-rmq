# stingar-rmq
RabbitMQ Proof of Concept for STINGAR project

Proof of concept architecture for replacing hpfeeds with ZeroMQ

## Building

Clone this repository to your local system.

Run the following command:

```
docker-compose up mongodb redis rabbitmq apiarist chnserver
```

Finally run the following command:

```
docker-compose up cowrie
```

You should find that the honeypot has registered to CHN Server, and after attempting to SSH to this container on localhost port 2222, you should see events in CHN Server.


## Pros and Cons

### Pros

* More robust architecture by replacing hpfeeds with a standard message queue
* AMQP Python Library allows us to move away from pyev and evnet
* AMQP model supports queues and topics in a simplified format
* Built in support for TLS authentication (not implemented in these containers yet)
* Easy communication between instances of CHN Server without relying on other services, such as CIF


### Cons

* More complex as it requires users to also maintain a RabbitMQ container
