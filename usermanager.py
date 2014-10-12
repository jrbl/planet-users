#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A PoC implementation of a user management service"""


import flask
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = flask.Flask(__name__)


@app.route('/users/<userid>', methods=['GET'])
def get_user(userid):
    """Return the matching user record or 404 if none exist."""
    app.logger.debug("get user")
    Flask.abort(404)
    return "TODO: called get_user"

@app.route('/users/<userid>', methods=['POST'])
def post_user(userid):
    """Create a new user record.
    
    The body of the request should be a valid user record. POSTs to an
    existing user are treated as errors and flagged with the appropriate
    HTTP status code.
    """
    app.logger.debug("post user")
    # FIXME: once appropriate HTTP status code is determined, update docstring
    Flask.abort(500) # XXX
    return "TODO: called post_user"

@app.route('/users/<userid>', methods=['DELETE'])
def delete_user(userid):
    """Delete a user record. Return 404 if the user doesn't exist."""
    app.logger.debug("delete user")
    Flask.abort(404) # XXX
    return "TODO: called delete_user"

@app.route('/users/<userid>', methods=['PUT'])
def put_user(userid):
    """Update an existing user record.
    
    The body of the request should be a valid user record. PUTs to a
    non-existant user should return a 404."""
    app.logger.debug("put user")
    Flask.abort(404)
    return "TODO: called put_user"

# TODO route /groups: GET POST DELETE PUT
@app.route('/groups/<group_name>', methods=['GET'])
def get_group(group_name):
    """Return a JSON list of userids containing the members of group_name.
    
    Should return a 404 if the group doesn't exist or has no members."""
    app.logger.debug("get group")
    Flask.abort(404)
    return "TODO: called get_group"

@app.route('/groups/<group_name>', methods=['POST'])
def post_group(group_name):
    """Create an empty group called group_name.
    
    POSTs to an existing group should be treated as errors and flagged with
    the appropriate HTTP status code.
    """
    app.logger.debug("post group")
    # FIXME: once appropriate HTTP status code is determined, update docstring
    Flask.abort(500) # XXX
    return "TODO: called post_group"

@app.route('/groups/<group_name>', methods=['PUT'])
def put_group(group_name):
    """
    Update the membership list for group_name.
    
    The request body should be a JSON list describing the group's members.
    """
    app.logger.debug("put group")
    return "TODO: called put_group"

@app.route('/groups/<group_name>', methods=['DELETE'])
def delete_group(group_name):
    """
    Remove all members from the named group.
    
    Should return a 404 for unknown groups.
    """
    app.logger.debug("delete group")
    Flask.abort(404)
    return "TODO: called put_group"

@app.errorhandler(404)
def error_page_not_found(error):
    app.logger.debug("404 error handler fired")
    return flask.render_template('404.html', error=error), 404


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
