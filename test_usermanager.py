#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for a PoC implementation of a user management service"""

import unittest

from flask import Flask

import usermanager


class UserMethodsTestCase(unittest.TestCase):
    """Tests ensuring proper functioning of the /usr/* endpoints"""

    # TODO: test GET, PUT, POST, DELETE
    def test_post_user(self):
        with usermanager.app.test_request_context('/users/', method='POST'):
            pass # FIXME TODO


# TODO: test class for Group methods

if __name__ == "__main__":
    # FIXME: this should run the tests
    #        use  test_request_context()
    pass
