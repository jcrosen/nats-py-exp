NATS-py-exp
~~~~~~~~~~~
This is an exploration and experiment in using `NATS`_ with python for asynchronous
messaging.

Installation
------------
- Ensure docker >=18 and docker-compose >= 1.23 are installed
- Clone this repository and then use the following

  ::

    docker-compose pull nats
    docker-compose build pubsub-base pubsub-http pubsub-dev


Usage
-----
First start the nats service
  ::

    docker-compose up -d nats

Basic time example
  ::

    docker-compose run --rm pubsub-scripts python scripts/subscribe_async.py

    # In another terminal
    docker-compose run --rm pubsub-scripts python scripts/publish_async.py

Customized producer/consumer example
  ::

    docker-compose run --rm pubsub-scripts python scripts/subscribe_async.py \
      --subject user-event \
      --handler scripts.subscribe_async.log_user_event

    # In another terminal
    docker-compose run --rm pubsub-scripts python scripts/publish_async.py \
      --subject user-event \
      --producer scripts.publish_async.user_event_producer

Extended consumers example
  ::

    # With the subscribe and publish scripts from above still running
    # In another terminal
    docker-compose run --rm pubsub-scripts python scripts/subscribe_async.py \
      --subject user-event \
      --handler scripts.subscribe_async.handle_user_account_events

    # In another terminal
    docker-compose run --rm pubsub-scripts python scripts/subscribe_async.py \
      --subject user-messages

Basic http example
  ::

    docker-compose up -d pubsub-http-api
    docker-compose run --rm pubsub-scripts python scripts/subscribe_async.py \
      --subject http-messages

    # In another terminal
    curl -XPOST http://localhost:5005/publish/http-messages -d 'Hello!'

Testing
-------
  ::

    docker-compose run --rm pubsub-test

.. _NATS: https://nats.io
