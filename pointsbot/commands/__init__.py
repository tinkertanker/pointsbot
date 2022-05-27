from typing import Union
# noinspection PyPackageRequirements
import discord
import numbers


def fmt_pts(usr_mention: str, points_num: Union[float, int]) -> str:
    """
    Formats the point result output for printing

    :param points_num: the number of points
    :param usr_mention: the mention
    :return: A formatted string
    """
    plural = "s" if points_num != 1 else ""
    return f"{usr_mention} now has **{points_num:.2f}** point{plural}."


def fmt_update_pts(usr_mention: str, delta: Union[float, int], new_pts: Union[float, int]) -> str:
    """
    Formats the point update result output for printing

    :param usr_mention: the mention
    :param delta: the delta
    :param new_pts: the new points
    :return: A formatted string
    """
    sign = "+" if delta > 0 else "-"
    return f"{usr_mention} now has **{new_pts:.2f}** point{'s' if new_pts != 1 else ''} " \
           f"({sign}{abs(delta):.2f})"


def fmt_spread_pts(role: discord.Role, total_pts: Union[float, int]) -> str:
    """
    Formats the point spread result output for printing
    Note that this assumes the spread is even.

    :param role: The role the points was spread amongst
    :param total_pts: The total number of points distributed
    :return: The formatted string
    """
    n_members = len(role.members)
    each_pts = total_pts / n_members
    plural_pts = "s" if total_pts != 1 else ""
    plural_members = "s" if n_members != 1 else ""
    action = "distributed" if total_pts > 0 else "deducted"
    sign = "+" if total_pts > 0 else "-"
    return f"Evenly {action} **{sign}{abs(total_pts):.2f}** point{plural_pts} to **{n_members}** user{plural_members}" \
           f" in {role.mention}. Each user received **{sign}{abs(each_pts):.2f}** points"
