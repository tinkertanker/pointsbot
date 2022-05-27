# noinspection PyPackageRequirements
import discord
# noinspection PyPackageRequirements
from discord.ext import commands

from pointsbot import PointsBot
from pointsbot.commands import fmt_pts
from pointsbot.database import fetch_points, fetch_top_n_users, fetch_history, HistoryEntry

import time


class Points(commands.Cog):
    def __init__(self, bot: PointsBot):
        self.bot = bot

    points = discord.SlashCommandGroup("points", "Points related commands.")

    @points.command(name='self', description="Retrieves your own points")
    async def points_self(self, ctx: discord.ApplicationContext):
        """
        Retrieves your own points.
        :param ctx: The application context
        :return: The number of points you have
        """
        if not isinstance(ctx.author, discord.Member):
            await ctx.respond("Cannot process this command", ephemeral=True)
            return
        points = fetch_points(ctx.author, self.bot.db)
        await ctx.respond(fmt_pts(ctx.author.mention, points), ephemeral=True)

    @points.command(name='history', description="See your points history")
    async def points_history(self, ctx: discord.ApplicationContext,
                             user: discord.Option(discord.SlashCommandOptionType.user,
                                                  "The user to view the history for",
                                                  required=False)):
        """
        Returns the history of your points changes

        :param user: The user to view the history for. Defaults to yourself if no user is specified.
        :param ctx: The application context
        :return: The history of all your points changes
        """

        def fmt_history(history: list[HistoryEntry]):
            storage = []
            for entry in history:
                # very awful, should've used an ORM
                disp_name = entry.user_display_name
                points_delta = entry.points_delta
                previous_value = entry.previous_value
                modifier_disp_name = entry.modifier_display_name
                timestamp = entry.utc_timestamp
                fmt_string = f"* {disp_name}'s points changed by {points_delta:.2f} from {previous_value:.2f} " \
                             f"by {modifier_disp_name} at <t:{timestamp}>"
                storage.append(fmt_string)
            return "\n".join(storage)

        usr: discord.Member = user or ctx.author
        hist = fetch_history(usr, self.bot.db)
        if not hist or len(hist) == 0:
            if usr is ctx.author:
                await ctx.respond("You have no points history...", ephemeral=True)
            else:
                await ctx.respond(f"{str(usr)} has no points history...", ephemeral=True)
            return
        # print(hist)
        await ctx.respond(fmt_history(hist), ephemeral=True)

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
    async def points_leaderboard(self, ctx: discord.ApplicationContext,
                                 num_users: discord.Option(discord.SlashCommandOptionType.integer,
                                                           "The number of users to retrieve", default=10)):
        """
        Retrieves the top N users with the most points

        Args:
            ctx: The application context
            num_users: The number of users to retrieve

        Returns:
              None

        """
        if num_users < 1:
            await ctx.respond("Nope. That's LITERALLY impossible.", ephemeral=True)
        top_users = fetch_top_n_users(ctx.guild, self.bot.db, num_users)
        if not top_users:
            await ctx.respond("There are no users with points.", ephemeral=True)
            return
        await ctx.respond("Leaderboard computed", embed=gen_leaderboard_embed(top_users))


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
        embed.add_field(name=f"#{i + 1}: {user_tag}", value=f"{points:.2f}", inline=False)
    embed.set_footer(text=f"© pointsbot")
    return embed


def setup(bot: PointsBot):
    bot.add_cog(Points(bot))
