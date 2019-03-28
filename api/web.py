"""
Minimal HTTP interface for publishing messages to NATS
"""

import os
import sys
sys.path.append(os.getcwd())

from flask import Flask, request

from pubsub.pubsub import blocking_publish

app = Flask(__name__)


@app.route('/publish/<subject>', methods=['POST'])
def publish(subject):
    data = request.get_data() or b''
    blocking_publish(subject, data=data)
    return ''
