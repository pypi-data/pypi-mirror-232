"""Tests for utils_base."""

import unittest

from utils_base import Log

from utils_twitter import Twitter
from utils_twitter.TwitterActionerMixinHelpers import (
    _update_profile_description, _update_status, _upload_media)

log = Log('test_twitter')

TEST_QUOTE = '\n'.join(
    [
        'Data is a precious thing',
        'and will last longer',
        'than the systems themselves.',
        '- Tim Berners-Lee',
    ]
)


SKIP_API_CREDENTIALS = 'Needs Twitter API credentials'


class TestActionerMixinHelpers(unittest.TestCase):
    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_update_status(self):
        twitter = Twitter.from_environ_vars()
        _update_status(twitter.api, TEST_QUOTE, [])

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_upload_media(self):
        twitter = Twitter.from_environ_vars()
        _upload_media(twitter.api, ['tests/data.png'])

    @unittest.skip(SKIP_API_CREDENTIALS)
    def test_update_profile_description(self):
        Twitter.from_environ_vars()
        _update_profile_description()
