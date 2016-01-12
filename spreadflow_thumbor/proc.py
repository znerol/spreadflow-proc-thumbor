from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import base64
import hashlib
import hmac
import os

class ThumborService(object):

    def __init__(self, thumborBaseUrl='http://localhost:8888/', thumborKey=None):
        self.thumborBaseUrl = thumborBaseUrl if isinstance(thumborBaseUrl, unicode) else thumborBaseUrl.decode('utf-8')

        if thumborKey:
            self.thumborKey = thumborKey if isinstance(thumborKey, bytes) else thumborKey.encode('utf-8')
        else:
            self.thumborKey = None

    def generate_url(self, operations, target_url):
        op = "/".join(operations + (target_url,))
        key = base64.urlsafe_b64encode(hmac.new(self.thumborKey, op.encode('utf-8'), hashlib.sha1).digest()) if self.thumborKey else 'unsafe'
        return self.thumborBaseUrl + key + u'/' + op


class ThumborUrlGenerator(object):

    def __init__(self, service, operations=('fit-in', '320x320'), key='content_url', destkey='thumbnail'):
        self.service = service
        self.operations = operations
        self.key = key
        self.destkey = destkey

    def __call__(self, item, send):
        for oid in item['inserts']:
            base = os.path.splitext(item['data'][oid][self.key])[0]
            filename = os.path.basename(base) + '.jpg'

            item['data'][oid][self.destkey] = {
                'url': self.service.generate_url(self.operations, item['data'][oid][self.key]),
                'filename': filename,
            }

        send(item, self)

    @property
    def dependencies(self):
        yield (self, self.service)
