from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import base64
import hashlib
import hmac
import os

class ThumborService(object):

    def __init__(self, thumborBaseUrl='http://localhost:8888/', thumborKey=None):
        self.thumborBaseUrl = thumborBaseUrl if isinstance(thumborBaseUrl, bytes) else thumborBaseUrl.encode('ascii')

        if thumborKey:
            self.thumborKey = thumborKey if isinstance(thumborKey, bytes) else thumborKey.encode('utf-8')
        else:
            self.thumborKey = None

    def generate_url(self, operations, target_url):
        operations = [op if isinstance(op, bytes) else op.encode('ascii') for op in operations]
        target_url = target_url if isinstance(target_url, bytes) else target_url.encode('ascii')
        operations.append(target_url)

        op = b'/'.join(operations)
        key = base64.urlsafe_b64encode(hmac.new(self.thumborKey, op, hashlib.sha1).digest()) if self.thumborKey else b'unsafe'
        return (self.thumborBaseUrl + key + b'/' + op).decode('ascii')


class ThumborUrlGenerator(object):

    def __init__(self, service, operations=('fit-in', '320x320'), key='content_url', destkey='thumbnail'):
        self.service = service
        self.operations = operations
        self.key = key
        self.destkey = destkey

    def __call__(self, item, send):
        for oid in item['inserts']:
            item['data'][oid][self.destkey] = self.service.generate_url(self.operations, item['data'][oid][self.key])

        send(item, self)

    @property
    def dependencies(self):
        yield (self, self.service)
