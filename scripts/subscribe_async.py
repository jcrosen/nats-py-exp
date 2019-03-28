import os
import sys
sys.path.append(os.getcwd())

from argparse import ArgumentParser
import asyncio
import importlib
import logging
import pprint

from pubsub.pubsub import ManagedAsyncPubsub, async_logging_handler
from pubsub.serialize import py_json_deserialize, py_json_serialize

logger = logging.getLogger(__name__)
DEFAULT_SUBJECT = 'time'
DEFAULT_WAIT = 3600


async def log_user_event(msg):
    logger.critical(pprint.pformat(
        py_json_deserialize(msg.data.decode())
    ))


async def handle_user_account_events(msg):
    data = py_json_deserialize(msg.data.decode())
    if data['event_type'] not in ('UserAccountCreated', 'UserAccountClosed'):
        return
    user_id = data['data']['user_id']
    phrase = 'Welcome' if data['event_type'].endswith('Created') else 'Goodbye'
    async with ManagedAsyncPubsub() as pubsub:
        await pubsub.publish(
            'user-messages'.format(user_id),
            reply='user-support'.format(user_id),
            data=py_json_serialize({
                'subject': '{}!'.format(phrase),
                'body': '{} user {}.'.format(phrase, user_id)
            }).encode()
        )


async def run(
    subject=DEFAULT_SUBJECT, wait=DEFAULT_WAIT, handler=async_logging_handler
):
    async with ManagedAsyncPubsub() as pubsub:
        await pubsub.subscribe(subject, handler=handler)
        await asyncio.sleep(wait)


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.arg = lambda *a, **k: parser.add_argument(*a, **k) and parser
    parser\
        .arg(
            '--subject',
            help='NATS Subject for the subscription',
            default='time'
        )\
        .arg(
            '--handler',
            help='Python import path to your handler function',
        )\
        .arg(
            '--wait',
            type=float,
            default=DEFAULT_WAIT,
            help='wait in seconds; decimal/float values allowed'
        )

    args = parser.parse_args()
    handler = async_logging_handler
    if args.handler:
        try:
            mod, fn = args.handler.rsplit('.', 1)
            handler = getattr(importlib.import_module(mod), fn)
        except Exception as e:
            logger.critical(
                'Unable to import handler {}: {}'.format(args.handler, str(e))
            )
            raise

    kwargs = {
        'subject': args.subject,
        'handler': handler,
        'wait': args.wait
    }
    logger.info('Starting subscription for {} seconds'.format(DEFAULT_WAIT))
    try:
        asyncio.run(run(**kwargs))
    except KeyboardInterrupt:
        pass
