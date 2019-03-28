import os
import sys
sys.path.append(os.getcwd())

from argparse import ArgumentParser
import asyncio
from datetime import datetime
import importlib
import logging
from random import random
from uuid import uuid4

from pubsub.pubsub import ManagedAsyncPubsub
from pubsub.serialize import py_json_serialize

logger = logging.getLogger(__name__)
DEFAULT_SUBJECT = 'time'
DEFAULT_WAIT = 5


async def user_event_producer():
    possible_events = [
        'UserAccountCreated', 'UserEmailVerified',
        'UserActivated', 'UserAccountClosed',
        'UserLoggedIn', 'UserLoggedIn', 'UserLoggedIn',
        'UserLoggedOut', 'UserLoggedOut', 'UserLoggedOut',
    ]
    while True:
        waiting = random() * 3
        event = possible_events[int(random() * len(possible_events))]
        await asyncio.sleep(waiting)
        yield py_json_serialize({
            'id': str(uuid4()),
            'ts': datetime.utcnow(),
            'event_type': event,
            'data': {
                'waited': round(waiting, 3),
                'user_id': str(uuid4()),
            }
        }).encode()


async def async_time_producer(wait=DEFAULT_WAIT):
    while True:
        yield datetime.utcnow().isoformat().encode()
        await asyncio.sleep(wait)


async def run(producer, subject=DEFAULT_SUBJECT):
    async with ManagedAsyncPubsub() as pubsub:
        async for data in producer():
            await pubsub.publish(subject, data=data)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.arg = lambda *a, **k: parser.add_argument(*a, **k) and parser
    parser\
        .arg(
            '--subject',
            help='NATS Subject for the subscription',
            default=DEFAULT_SUBJECT
        )\
        .arg(
            '--producer',
            help='Python import path to your producer function',
        )

    args = parser.parse_args()
    producer = async_time_producer
    if args.producer:
        try:
            mod, fn = args.producer.rsplit('.', 1)
            producer = getattr(importlib.import_module(mod), fn)
        except Exception as e:
            logger.critical(
                'Unable to import producer {}: {}'.format(args.producer, str(e))
            )
            raise

    kwargs = {
        'subject': args.subject,
        'producer': producer,
    }

    try:
        asyncio.run(run(**kwargs))
    except KeyboardInterrupt:
        pass
