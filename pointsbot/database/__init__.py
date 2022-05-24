from typing import Optional

import discord

from .sqlite_engine import SqliteEngine


def fmt_pts(usr_mention: str, points_num: int) -> str:
    """
    Formats the point result output for printing
    :param points_num: the number of points
    :param usr_mention: the mention
    :return: A formatted string
    """
    if points_num == 1:
        return f"{usr_mention} now has **{points_num}** point"
    else:
        return f"{usr_mention} now has **{points_num}** points"


def fetch_points(usr: discord.User, engine: SqliteEngine) -> int:
    """
    Attempts to the fetch the number of points a user has.
    If the user has no points, 0 is returned, and a database entry is created.

    :param usr: The user
    :param engine: Database engine
    :return: The number of points the user has
    """
    cur = engine.cur()
    results = cur.execute("SELECT points FROM points WHERE user_id = ?", (usr.id,)).fetchone()
    if results is None:
        cur.execute("INSERT INTO points (user_id, user_display_name, points) VALUES (?, ?, ?)",
                    (usr.id, str(usr), 0))
        engine.conn().commit()
        return 0

    return results[0]


def update_usr_points(usr: discord.User, update_val: int, engine: SqliteEngine) -> int:
    """
    Attempts to update the number of points a user has.
    If the user has no points, an entry is created for that user.

    Notes: This runs 3 SQL queries if the user is not tracked by the DB.
    If the user is tracked, it runs 2 queries.

    :param engine: The DB engine to use
    :param usr: The user
    :param update_val: The amount to update the points by
    :return: The updated points
    """
    cur = engine.cur()
    curr_pts = fetch_points(usr, engine)  # runs 1 or 2 queries
    new_pts = curr_pts + update_val
    cur.execute("UPDATE points SET points = ? WHERE user_id = ?", (new_pts, usr.id))
    engine.conn().commit()
    return new_pts


def set_points(usr: discord.User, points: int, engine: SqliteEngine) -> int:
    """
    Sets the number of points a user has.
    If the user has no points, an entry is created for that user.

    Notes: This runs 3 SQL queries if the user is not tracked by the DB.
    If the user is tracked, it runs 2 queries.

    :param engine: The DB engine to use
    :param usr: The user
    :param points: The number of points to set
    :return: The points the user now has
    """
    cur = engine.cur()
    fetch_points(usr, engine)  # runs 1 or 2 queries
    cur.execute("UPDATE points SET points = ? WHERE user_id = ?", (points, usr.id))
    engine.conn().commit()
    return points


def fetch_top_n_users(engine: SqliteEngine, n=10) -> Optional[list[tuple]]:
    """
    Fetches the top N users, ordering by the number of points they have.
    :param engine: The db engine
    :param n: The top N users to retrieve
    :return: list of (user_display_name, points) tuples, or none if there are no users
    """
    top_n = engine.cur() \
        .execute("SELECT user_display_name, points FROM points ORDER BY points DESC LIMIT ?", (n,)).fetchall()
    if top_n is None or len(top_n) == 0:
        return
    return top_n
