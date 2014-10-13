#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A PoC implementation of a user management service"""


from collections import defaultdict
import json

import flask
from flask import Flask


# FIXME: get these out of globals
app = flask.Flask(__name__)


# This should be a database of some kind, but for PoC, I didn't want to spend
# a lot of time teaching myself SQLAlchemy.
# FIXME: This would be a nicer proxy for a database if we had an object 
#        wrapper around these
USERS = dict()
GROUPS = defaultdict(set)
def _reset_db():
    """Reset the state of our nascent database to emptiness."""
    global USERS
    global GROUPS
    USERS = dict()
    GROUPS = defaultdict(set)

def _del_users_groups(userid):
    """Delete every reference to this user from all of the groups they belong to."""
    if userid in USERS:
        for groupname in USERS[userid].groups:
            GROUPS[groupname].remove(userid)
        USERS[userid].groups = []

def _del_groups_users(group_name):
    """Delete every reference to this group from all the users belonging to it."""
    # Cf. the note on the API call delete_group below; the spec is weird here.
    if group_name in GROUPS:
        for userid in GROUPS[group_name]:
            # Intentionally let ValueErrors bubble up to the user
            USERS[userid].groups.remove(group_name)
        GROUPS[group_name] = set()

def _add_user(user):
    """Add a user to the USERS set, keeping group members up to date."""
    # XXX: In a real database we'd accomplish this with a many-to-many relations and 
    # foreign key constraints. Here, we do it with a small amount of code.
    _del_users_groups(user.userid)  # make add_user() useful for adds or updates
    USERS[user.userid] = user
    for groupname in user.groups:
        GROUPS[groupname].add(user.userid)

def _add_group(group_name, members=set()):
    """Add a group to the GROUPS set, keeping user members up to date."""
    # XXX: In a real database we'd accomplish this with a many-to-many relations and 
    # foreign key constraints. Here, we do it with a small amount of code.
    _del_groups_users(group_name)  # make add_user() useful for adds or updates
    GROUPS[group_name] = members
    for user in GROUPS[group_name]:
        USERS[user].groups.append(group_name)
        
def _del_user(userid):
    """Remove a user from the USERS set, keeping group members up to date."""
    # XXX: In a real database we'd accomplish this with a many-to-many relations and 
    # foreign key constraints. Here, we do it with a small amount of code.
    _del_users_groups(userid)
    del USERS[userid]

def _dump_group(groupname):
    """Convenience function for producing JSON output of group info."""
    # XXX: If I were using an ORM there would be a Group model and it would have its own
    # to_json method, congruent with the User objects'
    return json.dumps(sorted(GROUPS[groupname]))


class User(object):
    def __init__(self, userid, firstname, lastname, groups):
        self.userid = userid
        self.firstname = firstname
        self.lastname = lastname
        self.groups = groups

    def __hash__(self):
        return self.userid

    def to_dict(self):
        return {'userid': self.userid, 
                'firstname': self.firstname,
                'lastname': self.lastname, 
                'groups': [g.name for g in self.groups]}

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, d):
        return cls(d['userid'], d['firstname'], d['lastname'], d['groups'])


@app.route('/users/<userid>', methods=['GET'])
def get_user(userid):
    """Return the matching user record or 404 if none exist."""
    app.logger.debug("get user {}".format(userid))
    if userid in USERS:
        return flask.Response(USERS[userid].to_json(), mimetype="application/json")
    flask.abort(404, {'method': 'GET', 'type': 'user'})

@app.route('/users/<userid>', methods=['POST'])
def post_user(userid):
    """Create a new user record.
    
    The body of the request should be a valid user record. POSTs to an
    existing user are treated as errors and flagged with a 403 Forbidden.
    """
    app.logger.debug("post user {}".format(userid))
    if userid in USERS:
        flask.abort(403, {'method': 'POST', 'type': 'user'})
    userinfo = flask.request.get_json(force=True)
    _add_user(User.from_dict(userinfo))
    return flask.Response(USERS[userid].to_json(), mimetype="application/json")

@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
    """Delete a user record. Return 404 if the user doesn't exist."""
    app.logger.debug("delete user")
    if userid in USERS:
        _del_user(userid)
        return flask.Response('{}', mimetype="application/json")
    flask.abort(404, {'method': 'DELETE', 'type': 'user'})

@app.route('/users/<userid>', methods=['PUT'])
def put_user(userid):
    """Update an existing user record.
    
    The body of the request should be a valid user record. PUTs to a
    non-existant user should return a 404."""
    app.logger.debug("put user")
    if userid in USERS:
        userinfo = flask.request.get_json(force=True)
        _add_user(User.from_dict(userinfo))
        return flask.Response(USERS[userid].to_json(), mimetype="application/json")
    flask.abort(404, {'method': 'PUT', 'type': 'user'})

# TODO route /groups: GET POST DELETE PUT
@app.route('/groups/<group_name>', methods=['GET'])
def get_group(group_name):
    """Return a JSON list of userids containing the members of group_name.
    
    Should return a 404 if the group doesn't exist or has no members."""
    app.logger.debug("get group")
    if group_name in GROUPS:
        return flask.Response(_dump_group(group_name), mimetype="application/json")
    flask.abort(404, {'method': 'GET', 'type': 'group'})

@app.route('/groups/<group_name>', methods=['POST'])
def post_group(group_name):
    """Create an empty group called group_name.
    
    POSTs to an existing group should be treated as errors and flagged with
    a 403 Forbidden.
    """
    app.logger.debug("post group")
    if group_name in GROUPS:
        flask.abort(403, {'method': 'POST', 'type': 'group'})
    _add_group(group_name)
    return flask.Response(_dump_group(group_name), mimetype="application/json")

@app.route('/groups/<group_name>', methods=['PUT'])
def put_group(group_name):
    """
    Update the membership list for group_name.
    
    The request body should be a JSON list describing the group's members.
    """
    app.logger.debug("put group")
    if group_name in GROUPS:
        userlist = flask.request.get_json(force=True)
        _add_group(group_name, members=set(userlist))
        return flask.Response(_dump_group(group_name), mimetype="application/json")
    flask.abort(404, {'method': 'PUT', 'type': 'group'})

@app.route('/groups/<group_name>', methods=['DELETE'])
def delete_group(group_name):
    """
    Remove all members from the named group.
    
    Should return a 404 for unknown groups.
    """
    # XXX: The spec is dubiously worded, speciying we only empty the group, meaning 
    #      we'll accumulate empty groups in our database over time without away to clean
    #      them up. A saner spec would have us remove empty groups altogether.
    app.logger.debug("delete group")
    if group_name in GROUPS:
        _del_groups_users(group_name)
        return flask.Response('[]', mimetype="application/json")
    flask.abort(404, {'method': 'DELETE', 'type': 'group'})


@app.errorhandler(403)
def error_(error):
    app.logger.debug("403 error handler fired")
    return flask.render_template('403.html', error=error.description), 403

@app.errorhandler(404)
def error_page_not_found(error):
    app.logger.debug("404 error handler fired")
    return flask.render_template('404.html', error=error.description), 404


if __name__ == "__main__":

    # configuration: TODO take on the command line via argparse
    db_path = '/tmp/usermanager_store.db'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///{}".format(db_path)
    DEBUG = True

    # FIXME: include doctests?
    if DEBUG:
        app.debug = True
        app.run()
    else:
        app.debug = False
        app.run(host='0.0.0.0')
