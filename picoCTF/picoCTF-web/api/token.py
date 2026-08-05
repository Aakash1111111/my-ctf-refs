"""
Module for token functionality.

Tokens act as a registry for storing arbitrary values associated with a user,
group, or other set of fields.
"""

import api


def get_token_path(token_name):
    """
    Format the token name into a token path.

    Returns:
      The token path

    """
    return "tokens.{}".format(token_name)


def set_token(key, token_name, token_value=None):
    """
    Set a token.

    Overwrites the existing token for a given key, if one exists.
    If a token value is not specified, a random value is generated.

    Args:
        key: the unique identifier object
        token_name: the name of the token to set
        token_value: optionally specify the value of the token
    Returns:
        The token value
    """
    db = api.db.get_conn()

    # Should never realistically collide.
    if token_value is None:
        token_value = api.common.hash(str(key) + api.common.token())

    db.tokens.update(
        key, {"$set": {get_token_path(token_name): token_value}}, upsert=True
    )

    return token_value


def delete_token(key, token_name):
    """
    Remove the specified token for the user.

    Args:
        key: the unique identifier object
        token_name: the name of the token
    """
    db = api.db.get_conn()

    db.tokens.update(key, {"$unset": {get_token_path(token_name): ""}})


def find_key(query, multi=False):
    """
    Find a key based on a particular query.

    Args:
        query: the mongo query
        multi: defaults to False, return at most one result
    """
    db = api.db.get_conn()

    find_func = db.tokens.find_one
    if multi:
        find_func = db.tokens.find

    return find_func(query)


def find_key_by_token(token_name, token_value):
    """
    Search the database for a user with a token_name token_value pair.

    Returns None if no matching user is found.

    Args:
        token_name: the name of the token
        token_value: the value of the token
    """
    db = api.db.get_conn()

    return db.tokens.find_one(
        {get_token_path(token_name): token_value}, {"_id": 0, "tokens": 0}
    )
