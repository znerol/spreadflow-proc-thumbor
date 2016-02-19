from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

from libthumbor import CryptoURL

class ThumborService(object):

    def __init__(self, baseurl='http://localhost:8888/', secretkey='MY_SECURE_KEY'):
        self.baseurl = baseurl.rstrip('/')
        self._urlgen = CryptoURL(key=secretkey)

    def generate_url(self, options):
        return self.baseurl + self._urlgen.generate(**options)


class ThumborUrlGenerator(object):

    def __init__(self, service, key='content_url', destkey='thumbnail', options=None, optionskey=None):
        self.service = service
        self.key = key
        self.destkey = destkey
        self.options = options
        self.optionskey = optionskey

        if not (self.options == None) ^ (self.optionskey == None):
            raise ValueError('Either options or optionskey is required')

    def __call__(self, item, send):
        for oid in item['inserts']:
            if self.options:
                options = self.options.copy()
            else:
                options = item['data'][oid][self.optionskey].copy()

            options['image_url'] = item['data'][oid][self.key]
            item['data'][oid][self.destkey] = self.service.generate_url(options)

        send(item, self)

    @property
    def dependencies(self):
        yield (self, self.service)
