import discord
from discord.ext import commands

from pointsbot import PointsBot
from pointsbot.commands import fmt_pts, fetch_points


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
        top_users = self.bot.db.cur().execute("SELECT user_display_name, points "
                                              "FROM points ORDER BY points DESC LIMIT 10")\
            .fetchall()
        if top_users is None or len(top_users) == 0:
            await ctx.respond("There are no users with points.")
            return
        response_msg = []
        for i, (discord_tag, points) in enumerate(top_users):
            response_msg.append(f"{i + 1}. {discord_tag} - {points}")
        await ctx.respond("\n".join(response_msg))


def setup(bot: PointsBot):
    bot.add_cog(Points(bot))
