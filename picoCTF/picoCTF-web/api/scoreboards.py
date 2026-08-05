"""
Module for dealing with scoreboards.

An event can have multiple scoreboards with different eligibility criteria.
A team is initially eligible to appear on any scoreboards for which
its founding member is eligible.

When a new member joins the team, the team's eligibility for a given scoreboard
will be revoked if the new member does not fit its criteria.
(However, by default, members are prevented from joining a team if doing
so would cause the team to lose any existing scoreboard eligibilities.)

Scoreboards can also have optional metadata, such as a sponsor, logo, etc.
"""

import api


def get_all_scoreboards():
    """Return a list of all scoreboards in the database."""
    db = api.db.get_conn()
    scoreboards = db.scoreboards.find({}, {"_id": False})
    if not scoreboards:
        return []
    else:
        return list(scoreboards)


def get_scoreboard(sid):
    """Return a scoreboard from the database, or None if it does not exist."""
    db = api.db.get_conn()
    return db.scoreboards.find_one({"sid": sid}, {"_id": False})


def add_scoreboard(
    name, eligibility_conditions=None, priority=1, sponsor=None, logo=None
):
    """
    Add a scoreboard to the database.

    Args:
        name (str): name of the scoreboard
        eligibility_conditions (dict): mongodb query to find eligible users
        priority (int): optional, determines scoreboard tab ordering
        sponsor (str): optional, sponsor of the scoreboard
        logo (str): optional, URL of a logo image for the scoreboard

    Returns:
        ID of the newly created scoreboard
    """
    if eligibility_conditions is None:
        eligibility_conditions = {}
    db = api.db.get_conn()
    sid = api.common.token()
    db.scoreboards.insert(
        {
            "sid": sid,
            "name": name,
            "eligibility_conditions": eligibility_conditions,
            "priority": priority,
            "sponsor": sponsor,
            "logo": logo,
        }
    )
    return sid


def is_eligible(user, scoreboard):
    """Determine whether a given user is eligible to appear on a scoreboard."""
    search_query = scoreboard["eligibility_conditions"]
    search_query["uid"] = user["uid"]
    db = api.db.get_conn()
    return db.users.find_one(search_query) is not None
