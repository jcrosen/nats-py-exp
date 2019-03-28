"""
Utilities for publishing messages to NATS
"""
from functools import partial
import logging

from pynats import NATSClient as BlockingNATSClient
from nats.aio.client import Client as AsyncNATSClient

logger = logging.getLogger(__name__)
DEFAULT_HOST = 'nats'
DEFAULT_PORT = '4222'


def generate_blocking_client(host=DEFAULT_HOST, port=DEFAULT_PORT):
    client = BlockingNATSClient('nats://{}:{}'.format(host, port))
    client.connect()
    return client


def blocking_publish(subject, data=b'', reply='', client=None):
    """
    Publish to a NATS subject with a blocking publisher
    """
    with BlockingManagedPubsub(client=client) as pubsub:
        pubsub.publish(subject, data=data, reply=reply)


def generate_blocking_publisher(subject, reply='', client=None):
    """
    Return a wrapping function around `blocking_publish` which accepts a payload
    """
    return partial(
        blocking_publish,
        subject,
        reply=reply,
        client=client
    )


def logging_handler(message):
    logger.critical('Received message on \'{}\': {}'.format(
        message.subject, message.data
    ))


class BlockingManagedPubsub(object):
    def __init__(self, client=None):
        self.client = client
        self.manage_client = not client
        self._subs = {}

    def setup(self):
        if not self.client:
            self.client = generate_blocking_client()

    def teardown(self):
        # Probably unnecessary as the clients and NATS will handle this
        # but illustrates how one might manage it more directly
        for subscriber_id in self._subs:
            try:
                self.client.unsubscribe(subscriber_id)
            except:
                pass
        if self.manage_client:
            self.client.close()

    def __enter__(self):
        try:
            self.setup()
        except Exception as e:
            logger.critical('Error entering pubsub: {}'.format(e))
            raise
        return self

    def __exit__(self, type, value, tb):
        try:
            self.teardown()
        except Exception as e:
            logger.critical('Error exiting pubsub: {}'.format(e))
            raise

    def publish(self, subject, data=b'', reply=''):
        self.client.publish(
            subject,
            reply=reply,
            payload=data
        )

    def subscribe(self, subject, handler=logging_handler):
        subscription = self.client.subscribe(subject, callback=handler)
        self._subs[subscription.sid] = subscription
        return subscription

    def unsubscribe(self, subscription):
        self.client.unsubscribe(subscription)
        del self._subs[subscription.sid]


async def generate_async_client(host=DEFAULT_HOST, port=DEFAULT_PORT):
    client = AsyncNATSClient()
    await client.connect('nats://{}:{}'.format(host, port))
    return client


async def async_logging_handler(message):
    logger.critical('Received message on \'{}\': {}'.format(
        message.subject, message.data
    ))


class ManagedAsyncPubsub(object):
    def __init__(self, client=None):
        self.client = client
        self.manage_client = not client

    async def setup(self):
        if not self.client:
            self.client = await generate_async_client()

    async def teardown(self):
        if self.manage_client:
            await self.client.close()

    async def __aenter__(self):
        try:
            await self.setup()
        except Exception as e:
            logger.critical('Error entering pubsub: {}'.format(e))
            raise
        return self

    async def __aexit__(self, type, value, tb):
        try:
            await self.teardown()
        except Exception as e:
            logger.critical('Error exiting pubsub: {}'.format(e))
            raise

    async def publish(self, subject, data=b'', reply=''):
        await self.client.publish_request(
            subject,
            reply,
            data
        )

    async def subscribe(self, subject, handler=async_logging_handler):
        return await self.client.subscribe(subject, cb=handler)

    async def unsubscribe(self, sid):
        return await self.client.unsubscribe(sid)


async def async_publish(subject, data=b'', reply='', client=None):
    async with ManagedAsyncPubsub(client=client) as pubsub:
        await pubsub.publish(subject, data=data, reply=reply)
