stomp, stomper, stompest!
=========================

stompest is a full-featured [STOMP](http://stomp.github.com/) [1.0](http://stomp.github.com//stomp-specification-1.0.html), [1.1](http://stomp.github.com//stomp-specification-1.1.html), and [1.2](http://stomp.github.com//stomp-specification-1.2.html) implementation for Python including both synchronous and asynchronous clients:

* The `sync.Stomp` client is dead simple. It does not assume anything about your concurrency model (thread vs process) or force you to use it any particular way. It gets out of your way and lets you do what you want.
* The `async.Stomp` client is based on [Twisted](http://twistedmatrix.com/), a very mature and powerful asynchronous programming framework. It supports destination specific message and error handlers (with default "poison pill" error handling), concurrent message processing, graceful shutdown, and connect and disconnect timeouts.

Both clients make use of a generic set of components in the `protocol` module each of which can be used independently to roll your own STOMP client:

* a wire-level STOMP frame parser `protocol.StompParser` and compiler `protocol.StompFrame`,
* a faithful implementation of the syntax of the STOMP protocol with a simple stateless function API in the `protocol.commands` module,
* a generic implementation of the STOMP session state semantics in `protocol.StompSession`, such as protocol version negotiation at connect time, heart-beating, transaction and subscription handling (including a generic subscription replay scheme which may be used to reconstruct the session's subscription state after a forced disconnect),
* and `protocol.StompFailoverTransport`, a [failover transport](http://activemq.apache.org/failover-transport-reference.html) URI scheme akin to the one used in ActiveMQ.

This package is thoroughly unit tested and production hardened for the functionality used by the current maintainer and by [Mozes](http://www.mozes.com/) --- persistent queueing on [ActiveMQ](http://activemq.apache.org/). Minor enhancements may be required to use this STOMP adapter with other brokers.

Installation
============

* If you do not wish to use the asynchronous client (which depends on Twisted), stompest is fully self-contained.
* You can find all stompest releases on the [Python Package Index](http://pypi.python.org/pypi/stompest/). Just use the method you like most: `easy_install stompest`, `pip install stompest`, or `python setup.py install`.

Documentation & Code Examples
=============================
The stompest API is fully documented [here](http://nikipore.github.com/stompest/).

Questions or Suggestions?
=========================
Feel free to open an issue [here](https://github.com/nikipore/stompest/issues/) or post a question on the [forum](http://groups.google.com/group/stompest/).

Features
========

Commands layer
--------------
* Transport and client agnostic.
* Full-featured implementation of all STOMP client commands.
* Client-side handling of STOMP commands received from the broker.
* Stateless and simple function API.

Session layer
-------------
* Manages the state of a connection.
* Replays subscriptions upon reconnect.
* Heart-beat handling.

Failover layer
--------------
* Mimics the [failover transport](http://activemq.apache.org/failover-transport-reference.html) behavior of the native ActiveMQ Java client.
* Produces a (possibly infinite) sequence of broker network addresses and connect delay times.

Parser layer
------------
* Abstract frame definition.
* Transformation between these abstract frames and a wire-level byte stream of STOMP frames.

Clients
=======

`sync`
------
* Built on top of the abstract layers, the synchronous client adds a TCP connection (with SSL support) and a synchronous API.
* The concurrency scheme (synchronous, threaded, ...) is free to choose by the user.

`async`
-------
* Based on the Twisted asynchronous framework, including TCP connectivity (with SSL support).
* Fully unit-tested including a simulated STOMP broker.
* Graceful shutdown: on disconnect or error, the client stops processing new messages and waits for all outstanding message handlers to finish before issuing the `DISCONNECT` command.
* Error handling - fully customizable on a per-subscription level:
    * Disconnect: if you do not configure an errorDestination and an exception propagates up from a message handler, then the client will gracefully disconnect. This is effectively a `NACK` for the message (actually, disconnecting is the only way to `NACK` in STOMP 1.0). You can [configure ActiveMQ](http://activemq.apache.org/message-redelivery-and-dlq-handling.html) with a redelivery policy to avoid the "poison pill" scenario where the broker keeps redelivering a bad message infinitely.
    * Default error handling: passing an error destination parameter at subscription time will cause unhandled messages to be forwarded to that destination and then `ACK`ed.
    * Custom hook: you can override the default behavior with any customized error handling scheme.
* Separately configurable timeouts for wire-level connection, the broker's `CONNECTED` reply frame, and graceful disconnect (in-flight handlers that do not finish in time).

Acknowledgements
================
* Version 1.x of stompest was written by [Roger Hoover (@theduderog)](http://github.com/theduderog) at [Mozes](http://www.mozes.com/) and deployed in their production environment.
* Kudos to [Oisin Mulvihill](https://github.com/oisinmulvihill), the developer of [stomper] (https://github.com/oisinmulvihill/stomper)! His idea of an abstract representation of the STOMP protocol lives on in stompest.

Caveats
=======
* Requires Python 2.7. Not yet tested with Python 3.x.
* This package is thoroughly unit tested and production hardened for the functionality used by the current maintainer and by [Mozes](http://www.mozes.com/) --- persistent queueing on [ActiveMQ](http://activemq.apache.org/). It is tested with Python 2.7, Twisted 15 (it should work with Twisted 10.1 and higher), ActiveMQ 5.13 (it should work with 5.5.1 and higher), and [Apollo](http://activemq.apache.org/apollo/) 1.6. Some of the integration tests also pass against [RabbitMQ](http://www.rabbitmq.com/) 3.0.2 (RabbitMQ does not support all extended STOMP features). All of these brokers were tested with STOMP protocols 1.0, 1.1, and 1.2 (if applicable).  Minor enhancements may be required to use this STOMP adapter with other brokers.

To Do
=====
* see [proprosed enhancements](https://github.com/nikipore/stompest/issues?labels=enhancement&state=open)
