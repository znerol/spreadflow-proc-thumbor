from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import copy

from twisted.internet import defer

from mock import Mock
from testtools import ExpectedException, TestCase, run_test_with
from testtools.twistedsupport import AsynchronousDeferredRunTest

from spreadflow_core.scheduler import Scheduler
from spreadflow_delta.test.matchers import MatchesSendDeltaItemInvocation

from spreadflow_thumbor.proc import ThumborService, ThumborUrlGenerator


class SpreadflowThumborServiceTestCase(TestCase):

    def test_generate_hmac_url(self):
        srv = ThumborService(baseurl='https://thumbor-service/subdir/', secretkey='secret')
        expected = 'https://thumbor-service/subdir/P7hdoki2Gql1i9_XIb8pRIVPSHI=/fit-in/1024x1024/http://example.com/path/to/image.jpg'
        options = {'fit_in': True, 'width': '1024', 'height': 1024, 'image_url': 'http://example.com/path/to/image.jpg'}
        result = srv.generate_url(options)
        self.assertEquals(result, expected)


class SpreadflowThumborUrlGeneratorTest(TestCase):

    @run_test_with(AsynchronousDeferredRunTest)
    @defer.inlineCallbacks
    def test_static_options(self):
        generated_url = 'https://thumbor-service/subdir/P7hdoki2Gql1i9_XIb8pRIVPSHI=/fit-in/1024x1024/http://example.com/path/to/image.jpg'

        srv = Mock(spec=ThumborService)
        srv.generate_url.return_value = generated_url

        options = {'fit_in': True, 'width': '1024', 'height': 1024}
        gen = ThumborUrlGenerator(srv, options=options)

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
        expected_options = {
            'fit_in': True,
            'width': '1024',
            'height': 1024,
            'image_url': 'http://example.com/path/to/image.jpg'
        }
        srv.generate_url.assert_called_once_with(expected_options)

    @run_test_with(AsynchronousDeferredRunTest)
    @defer.inlineCallbacks
    def test_dynamic_options(self):
        generated_url = 'https://thumbor-service/subdir/P7hdoki2Gql1i9_XIb8pRIVPSHI=/fit-in/1024x1024/http://example.com/path/to/image.jpg'

        srv = Mock(spec=ThumborService)
        srv.generate_url.return_value = generated_url

        gen = ThumborUrlGenerator(srv, key='custom_url', destkey='custom_dest', optionskey='thumbor_options')

        options = {'fit_in': True, 'width': '1024', 'height': 1024}
        item = {
            'inserts': ['a'],
            'deletes': [],
            'data': {
                'a': {
                    'thumbor_options': options,
                    'custom_url': 'http://example.com/path/to/image.jpg',
                }
            }
        }

        expected = copy.deepcopy(item)
        expected['data']['a']['custom_dest'] = generated_url

        send_matcher = MatchesSendDeltaItemInvocation(expected, gen)
        send = Mock(spec=Scheduler.send)
        yield gen(item, send)
        self.assertEquals(send.call_count, 1)
        self.assertThat(send.call_args, send_matcher)
        expected_options = {
            'fit_in': True,
            'width': '1024',
            'height': 1024,
            'image_url': 'http://example.com/path/to/image.jpg'
        }
        srv.generate_url.assert_called_once_with(expected_options)

    def test_fail_if_constructed_with_dynamic_and_static_options(self):
        srv = Mock(spec=ThumborService)
        with ExpectedException(ValueError, 'Either options or optionskey is required'):
            ThumborUrlGenerator(srv, options={}, optionskey='thumbor_options')

    def test_fail_if_constructed_with_no_options(self):
        srv = Mock(spec=ThumborService)
        with ExpectedException(ValueError, 'Either options or optionskey is required'):
            ThumborUrlGenerator(srv)
