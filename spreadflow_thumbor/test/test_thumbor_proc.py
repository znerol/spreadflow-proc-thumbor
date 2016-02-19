from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import copy

from twisted.internet import defer

from mock import Mock
from testtools import TestCase, run_test_with
from testtools.twistedsupport import AsynchronousDeferredRunTest

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_thumbor.proc import ThumborService, ThumborUrlGenerator


class SpreadflowThumborServiceTestCase(TestCase):

    def test_generate_unsafe_url(self):
        srv = ThumborService()
        expected = 'http://localhost:8888/unsafe/fit-in/1024x1024/http://example.com/path/to/image.jpg'
        result = srv.generate_url(('fit-in', '1024x1024'), 'http://example.com/path/to/image.jpg')
        self.assertEquals(result, expected)

    def test_generate_hmac_url(self):
        srv = ThumborService(thumborBaseUrl='https://thumbor-service/subdir/', thumborKey='secret')
        expected = 'https://thumbor-service/subdir/P7hdoki2Gql1i9_XIb8pRIVPSHI=/fit-in/1024x1024/http://example.com/path/to/image.jpg'
        result = srv.generate_url(('fit-in', '1024x1024'), 'http://example.com/path/to/image.jpg')
        self.assertEquals(result, expected)


class SpreadflowThumborUrlGeneratorTest(TestCase):

    @run_test_with(AsynchronousDeferredRunTest)
    @defer.inlineCallbacks
    def test_proc(self):
        generated_url = 'https://thumbor-service/subdir/P7hdoki2Gql1i9_XIb8pRIVPSHI=/fit-in/1024x1024/http://example.com/path/to/image.jpg'

        srv = Mock(spec=ThumborService)
        srv.generate_url.return_value = generated_url

        gen = ThumborUrlGenerator(srv, operations=('fit-in', '1024x1024'))

        item = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'content_url': 'http://example.com/path/to/image.jpg',
                }
            }
        }

        expected = copy.deepcopy(item)
        expected['data']['a']['thumbnail'] = generated_url

        send_matcher = MatchesSendDeltaItemInvocation(expected, gen)
        send = Mock(spec=Scheduler.send)
        yield gen(item, send)
        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, send_matcher)
        srv.generate_url.assert_called_once_with(('fit-in', '1024x1024'), 'http://example.com/path/to/image.jpg')
