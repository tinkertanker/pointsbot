import datetime
import time
from collections import namedtuple
from typing import Optional, Union

# noinspection PyPackageRequirements
import discord

from .sqlite_engine import SqliteEngine


def track(usr: discord.Member, previous_points: Union[int, float],
          points_delta: Union[int, float],
          executor: discord.Member, engine: SqliteEngine):
    """
    Tracks a point change in the database history

    :param usr: The user the action was applied to
    :param previous_points: The previous points the user had
    :param points_delta: The points the user gained or lost
    :param executor: The user who executed the action
    :param engine: The DB engine
    :return: None
    """
    cur = engine.cur
    # now = datetime.datetime.utcnow()
    cur.execute(
        "INSERT INTO history (user_id,"
        " user_display_name,"
        " server_id,"
        " points_delta,"
        " previous_value,"
        " modifier_id,"
        " modifier_display_name,"
        " timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (usr.id,
         str(usr),
         usr.guild.id,
         points_delta,
         previous_points,
         executor.id,
         str(executor),
         int(time.time()))
    )
    engine.conn.commit()


HistoryEntry = namedtuple('HistoryEntry',
                          ['database_id',
                           'user_id',
                           'user_display_name',
                           'server_id',
                           'points_delta',
                           'previous_value',
                           'modifier_id',
                           'modifier_display_name',
                           'utc_timestamp'])


def fetch_history(usr: discord.Member, engine: SqliteEngine) -> Optional[list[HistoryEntry]]:
    """
    Fetches the history of a user.

    :param usr: The user
    :param engine: The DB engine to use
    :return: The history of the user.
     None if the user has no history (or history has been reset).
     If the user has a history, it is returned as a list of tuples.

    """
    cur = engine.cur
    results = cur.execute("SELECT * FROM history "
                          "WHERE user_id = ? AND server_id = ? "
                          "ORDER BY timestamp DESC",
                          (usr.id, usr.guild.id)).fetchall()

    if results or len(results) > 0:
        return [HistoryEntry(*row) for row in results]
    return None


def fetch_points(usr: discord.Member, engine: SqliteEngine) -> Union[int, float]:
    """
    Attempts to the fetch the number of points a user has.
    If the user has no points, 0 is returned, and a database entry is created.

    :param usr: The user
    :param engine: Database engine
    :return: The number of points the user has
    """
    cur = engine.cur

    results = cur.execute("SELECT points FROM points "
                          "WHERE user_id = ? AND server_id = ?",
                          (usr.id, usr.guild.id)).fetchone()
    if results is None:
        cur.execute("INSERT INTO points (user_id, server_id, user_display_name, points) "
                    "VALUES (?, ?, ?, ?)",
                    (usr.id, usr.guild.id, str(usr), 0))
        engine.conn.commit()
        return 0

    return results[0]


def update_usr_points(usr: discord.Member,
                      executor: discord.Member,
                      update_val: Union[int, float],
                      engine: SqliteEngine) -> Union[int, float]:
    """
    Attempts to update the number of points a user has.
    If the user has no points, an entry is created for that user.

    Notes: This runs 3 SQL queries if the user is not tracked by the DB.
    If the user is tracked, it runs 2 queries.

    :param executor: The user who executed the command
    :param engine: The DB engine to use
    :param usr: The user
    :param update_val: The amount to update the points by
    :return: The points the user now has
    """
    cur = engine.cur
    curr_pts = fetch_points(usr, engine)  # runs 1 or 2 queries
    new_pts = curr_pts + update_val
    cur.execute("UPDATE points SET points = ? "
                "WHERE user_id = ? AND server_id = ?", (new_pts, usr.id, usr.guild.id))
    track(usr, curr_pts, update_val, executor, engine)
    engine.conn.commit()
    return new_pts


def set_usr_points(usr: discord.Member,
                   executor: discord.Member,
                   points: Union[int, float],
                   engine: SqliteEngine) -> Union[int, float]:
    """
    Sets the number of points a user has.
    If the user has no points, an entry is created for that user.

    Notes: This runs 3 SQL queries if the user is not tracked by the DB.
    If the user is tracked, it runs 2 queries.

    :param executor: The user who executed the command
    :param engine: The DB engine to use
    :param usr: The user
    :param points: The number of points to set
    :return: The points the user now has
    """
    cur = engine.cur
    prev_pts = fetch_points(usr, engine)  # runs 1 or 2 queries
    cur.execute("UPDATE points SET points = ? "
                "WHERE user_id = ? AND server_id = ?", (points, usr.id, usr.guild.id))
    track(usr, prev_pts, points - prev_pts, executor, engine)
    engine.conn.commit()
    return points


def reset_all(server: Union[discord.Guild, int], engine: SqliteEngine):
    """
    Resets ALL points in a server to 0.

    :param server: The guild to reset the points for
    :param engine: The DB engine to use
    :return: None
    """
    guild_id = server.id if isinstance(server, discord.Guild) else server
    engine.cur.execute("UPDATE points SET points = 0 WHERE server_id = ?", (guild_id,))
    engine.cur.execute("DELETE FROM history WHERE server_id = ?", (guild_id,))
    engine.conn.commit()


def fetch_top_n_users(server: Union[discord.Guild, int], engine: SqliteEngine, n=10) -> Optional[list[tuple]]:
    """
    Fetches the top N users, ordering by the number of points they have.

    :param server: The guild to fetch the top N members from
    :param engine: The db engine
    :param n: The top N users to retrieve
    :return: list of (user_display_name, points) tuples, or none if there are no users
    """
    guild_id = server.id if isinstance(server, discord.Guild) else server
    top_n = engine.cur.execute("SELECT user_display_name, points FROM points "
                               "WHERE server_id = ? "
                               "ORDER BY points DESC LIMIT ?",
                               (guild_id, n)).fetchall()
    if top_n is None or len(top_n) == 0:
        return None
    return top_n
