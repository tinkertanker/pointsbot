# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from pointsbot import PointsBot
from pointsbot.commands import fmt_pts
from pointsbot.database import fetch_points, fetch_top_n_users

import time


class Points(commands.Cog):
    def __init__(self, bot: PointsBot):
        self.bot = bot

    points = discord.SlashCommandGroup("points", "Points related commands.")

    @points.command(name='self', description="Retrieves your own points")
    async def points_self(self, ctx: discord.ApplicationContext):
        """
        Retrieves your own points.
        :param ctx: The applicationcontext
        :return: The number of points you have
        """
        points = fetch_points(ctx.author, self.bot.db)
        await ctx.respond(fmt_pts(ctx.author.mention, points))

    @points.command(name="get", description="Retrieves the points of another user")
    async def points_get(self, ctx: discord.ApplicationContext,
                         user: discord.Option(discord.SlashCommandOptionType.user, "The user to retrieve points for")):
        # note: the description MUST be specified under discord.Option, otherwise the docstring introspection fails
        # this is a bug with py-cord
        """
        Retrieves the points of another user.
        :param ctx: The application context
        :param user: The user to retrieve points for
        :return: The number of points the user has
        """
        points = fetch_points(user, self.bot.db)
        await ctx.respond(fmt_pts(user.mention, points))

    @points.command(name="top", description="Retrieves the top 10 users with the most points")
    async def points_leaderboard(self, ctx: discord.ApplicationContext):
        """
        Retrieves the top 10 users with the most points
        :param ctx:
        :return:
        """
        top_users = fetch_top_n_users(self.bot.db)
        if not top_users:
            await ctx.respond("There are no users with points.")
            return
        await ctx.respond(embed=gen_leaderboard_embed(top_users))


def gen_leaderboard_embed(top_users: list[tuple]) -> discord.Embed:
    """
    Generates the leaderboard embed
    Please truncate the top users to 10, else the embed will be too big

    :param top_users: The top users, retrieved from the database.
    :return:
    """
    curr_time = int(time.time())
    embed = discord.Embed(title="View the spreadsheet", url="https://points.bot",
                          description=f"Generated by **pointsbot** at <t:{curr_time}>", color=0xf66151)
    embed.set_author(name="Points Leaderboard")
    for i, (user_tag, points) in enumerate(top_users):
        embed.add_field(name=f"#{i+1}: {user_tag}", value=f"{points:.2f}", inline=False)
    embed.set_footer(text=f"© pointsbot")
    return embed


def setup(bot: PointsBot):
    bot.add_cog(Points(bot))
