#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for a PoC implementation of a user management service"""

import json
import unittest

import usermanager


def _def_user(name, groups=[]):
    """Define a default user description."""
    return {name: usermanager.User(name, name, name, groups)}


class UserAPITestCase(unittest.TestCase):
    """Tests ensuring proper functioning of the /users/* endpoints"""

    no_users = {}
    one_user_no_groups = _def_user('user1')
    one_user_one_group = _def_user('user1', ['group1'])

    def setUp(self):
        usermanager.app.config['TESTING'] = True
        self.app = usermanager.app.test_client()

    def test_get_user_empty_404s(self):
        """A GET against an empty user database 404s."""
        usermanager.USERS = self.no_users.copy()
        rv = self.app.get('/users/user1')
        self.assertEquals(404, rv.status_code)

    def test_get_user_single(self):
        """GETs against a single user database 404 for missing users."""
        usermanager.USERS = self.one_user_no_groups.copy()
        test_username, test_userinfo = usermanager.USERS.items()[0]
        rv = self.app.get('/users/%s' % (test_username))
        self.assertEquals(200, rv.status_code)
        self.assertEquals(json.loads(rv.data), test_userinfo.to_dict())
        rv = self.app.get('/users/%s_notfound' % (test_username))
        self.assertEquals(404, rv.status_code)

    def test_post_user_to_self_403s(self):
        """A POST of a user against herself is forbidden"""
        usermanager.USERS = self.one_user_no_groups.copy()
        test_username, test_userinfo = usermanager.USERS.items()[0]
        rv = self.app.post('/users/%s' % (test_username),
                           data=test_userinfo.to_dict(),
                           content_type='application/json')
        self.assertEquals(403, rv.status_code)

    def test_post_user_empty_OK(self):
        """A POST against an empty user database is fine."""
        usermanager.USERS = self.no_users.copy()
        test_userinfo = _def_user('user1', [])['user1']
        rv = self.app.post('/users/user1',
                           data=test_userinfo.to_json(),
                           content_type='application/json')
        self.assertEquals(200, rv.status_code)
        self.assertEquals(json.loads(rv.data), test_userinfo.to_dict())

    def test_delete_user_empty_404s(self):
        """A DELETE with a user not in the database raises a 404."""
        usermanager.USERS = self.no_users.copy()
        rv = self.app.delete('/users/user1')
        self.assertEquals(404, rv.status_code)

    def test_delete_user_single(self):
        """A DELETE with a valid user in the database deletes them."""
        usermanager.USERS = self.one_user_no_groups.copy()
        test_username, test_userinfo = usermanager.USERS.items()[0]
        rv = self.app.delete('/users/%s' % (test_username))
        self.assertEquals(200, rv.status_code)
        self.assertEquals(json.loads(rv.data), {})
        self.assertEquals(usermanager.USERS, {})

    def test_put_user_empty_404s(self):
        """A PUT against a user not present in the database raises a 404."""
        usermanager.USERS = self.no_users.copy()
        test_userinfo = _def_user('user1', [])['user1']
        rv = self.app.put('/users/user1',
                          data=test_userinfo.to_json(),
                          content_type='application/json')
        self.assertEquals(404, rv.status_code)

    def test_put_valid_user_updates(self):
        """A PUT against existing user changes their values."""
        usermanager.USERS = self.one_user_no_groups.copy()
        test_username, test_userinfo = usermanager.USERS.items()[0]
        test_userinfo_dict = test_userinfo.to_dict()
        target_userinfo_dict = test_userinfo_dict.copy()
        target_userinfo_dict.update({'firstname': 'roberta',
                                     'lastname': 'builder'})
        rv = self.app.put('/users/user1',
                          data=json.dumps(target_userinfo_dict),
                          content_type='application/json')
        self.assertNotEquals(test_userinfo_dict, target_userinfo_dict)
        self.assertNotEquals(json.loads(rv.data), test_userinfo_dict)
        self.assertEquals(json.loads(rv.data), target_userinfo_dict)
        self.assertEquals(200, rv.status_code)


class GroupAPITestCase(unittest.TestCase):
    """Tests ensuring proper functioning of the /groups/* endpoints"""

    no_users = {}

    def setUp(self):
        usermanager.app.config['TESTING'] = True
        self.app = usermanager.app.test_client()

    def test_get_group_empty_users_404s(self):
        """A GET against an empty user database 404s."""
        usermanager.USERS = self.no_users.copy()
        rv = self.app.get('/groups/group1')
        self.assertEquals(404, rv.status_code)

    def test_get_group_single(self):
        """A GET against a single user database returns that user's groups."""
        usermanager.USERS = {}
        # one user with many groups
        usermanager._add_user(usermanager.User('user1', '', '',
                                               groups=['group1', 'group2']))
        test_username, test_userinfo = usermanager.USERS.items()[0]
        self.assertIsNot(len(test_userinfo.groups), 0)
        for group in test_userinfo.groups:
            rv = self.app.get('/groups/%s' % (group))
            self.assertEquals(200, rv.status_code)
            self.assertEquals(json.loads(rv.data), [test_username])

    def test_get_group_multiple(self):
        """A GET against a many user database returns those users' groups."""
        test_users = ['user1', 'user2', 'user3']
        test_group = 'group'
        usermanager._reset_db()
        # Many users with one group
        for u in test_users:
            usermanager._add_user(usermanager.User(u, '', '',
                                                   groups=[test_group])),
        self.assertIs(len(usermanager.GROUPS), 1)
        rv = self.app.get('/groups/%s' % (test_group))
        self.assertEquals(200, rv.status_code)
        self.assertEquals(json.loads(rv.data), sorted(test_users))

    def test_post_group_single(self):
        """A POST against the single group in a database raises a 403"""
        usermanager._reset_db()
        usermanager._add_user(usermanager.User('user1', '', '',
                                               groups=['group1'])),
        rv = self.app.post('/groups/%s' % ('group1'))
        self.assertEquals(403, rv.status_code)

    def test_post_group_empty(self):
        """A POST against the single group in a database raises a 403"""
        usermanager._reset_db()
        rv = self.app.post('/groups/%s' % ('group1'))
        self.assertEquals(200, rv.status_code)
        self.assertEquals(json.loads(rv.data), [])

    def test_put_group_empty(self):
        """A PUT against an empty group database 404s"""
        usermanager._reset_db()
        rv = self.app.put('/groups/%s' % ('group1'),
                          data=json.dumps([]),
                          content_type='application/json')
        self.assertEquals(404, rv.status_code)

    def test_put_group_many(self):
        """A PUT against a many-user group database updates them all"""
        usermanager._reset_db()
        test_users = [('user1', ['group1', 'group2']),
                      ('user2', ['group1']),
                      ('user3', ['group3'])]
        test_group = 'group2'
        # Many users with one group
        for u, gs in test_users:
            usermanager._add_user(usermanager.User(u, '', '', groups=gs)),
        rv = self.app.put('/groups/%s' % (test_group),
                          data=json.dumps([u[0] for u in test_users]),
                          content_type='application/json')
        self.assertEquals(200, rv.status_code)
        for user in usermanager.USERS:
            self.assertIn(test_group, usermanager.USERS[user].groups)

    def test_delete_group_empty(self):
        """A DELETE against an empty group database 404s"""
        usermanager._reset_db()
        rv = self.app.delete('/groups/%s' % ('group1'))
        self.assertEquals(404, rv.status_code)

    def test_delete_group_single(self):
        """A DELETE against a many-user group empties the group."""
        usermanager._reset_db()
        test_users = ['user1', 'user2', 'user3']
        test_group = 'group2'
        # Many users with one group
        for u in test_users:
            usermanager._add_user(usermanager.User(u, '', '',
                                                   groups=[test_group])),
        self.assertIs(len(usermanager.GROUPS), 1)
        self.assertIs(len(usermanager.USERS), 3)
        self.assertIs(len(usermanager.GROUPS[test_group]), 3)
        rv = self.app.delete('/groups/%s' % (test_group))
        self.assertEquals(200, rv.status_code)
        self.assertEquals(json.loads(rv.data), [])
        self.assertIs(len(usermanager.GROUPS), 1)
        self.assertIs(len(usermanager.USERS), 3)
        self.assertIs(len(usermanager.GROUPS[test_group]), 0)
        for u in test_users:
            self.assertEqual(usermanager.USERS[u].groups, [])

if __name__ == "__main__":
    unittest.main()
