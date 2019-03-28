"""
Integration tests for NATS pubsub
"""
import threading
import time
from unittest import TestCase

from pynats import NATSClient as BlockingNATSClient

from pubsub import pubsub


class TestBlockingManagedPubsub(TestCase):
    """
    Test BlockingManagedPubsub
    """

    def test_generate_blocking_client(self):
        client = pubsub.generate_blocking_client()
        assert isinstance(client, BlockingNATSClient)
        client.close()

    def test_blocking_publish(self):
        subject = 'test-subject'
        data = b'dataz'
        received = []

        def _handler(msg):
            nonlocal received
            received.append(msg)

        def subscriber():
            nonlocal received
            with pubsub.BlockingManagedPubsub() as _pubsub:
                _pubsub.subscribe(subject, _handler)
                _pubsub.client.wait(count=2)

        t = threading.Thread(target=subscriber)
        t.start()
        time.sleep(1)

        # Test the context manager
        with pubsub.BlockingManagedPubsub() as _pubsub:
            _pubsub.publish(subject, data)

        # Test the utility wrapper
        pubsub.blocking_publish(subject, data)

        t.join()

        assert len(received) == 2


# TODO
class TestAsyncManagedPubsub(TestCase):
    """
    Test BlockingManagedPubsub
    """

    pass
